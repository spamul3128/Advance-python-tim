import discord
import os
import re
from typing import Optional
from discord.ext import commands
from dotenv import load_dotenv
from database import db_manager
from llm import llm_service
from datetime import datetime, timedelta, UTC

# Load environment variables from .env file
load_dotenv()

# Set up Discord bot with message content intent and '!' prefix
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

bot = commands.Bot(command_prefix='!', intents=intents)

# Helper to parse timeframe strings like "1h", "24h", "7d" (also supports minutes via "Xm")
def _parse_duration_to_since(s: str) -> Optional[datetime]:
    try:
        s = s.strip().lower()
        if not s:
            return None
        if s.endswith("h"):
            hours = int(s[:-1])
            return datetime.now(UTC) - timedelta(hours=hours)
        if s.endswith("d"):
            days = int(s[:-1])
            return datetime.now(UTC) - timedelta(days=days)
        if s.endswith("m"):
            minutes = int(s[:-1])
            return datetime.now(UTC) - timedelta(minutes=minutes)
        return None
    except Exception:
        return None

@bot.event
async def on_ready():
    """Called when the bot successfully connects to Discord"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot ID: {bot.user.id}')

    # Initialize database connection
    print("📊 Initializing database connection...")
    success = await db_manager.initialize()
    if success:
        await db_manager.create_tables()
        total_messages = await db_manager.get_message_count()
        print(f"📈 Database ready! Total messages stored: {total_messages}")
    else:
        print("⚠️  Database connection failed. Messages will only be logged to console.")

    print('🎧 Listening for messages...')

# !history command: fetch past messages by user and/or channel with limit/timeframe
@bot.command(name="history", help="Get recent messages from the database. Usage: !history [options]\nOptions: user:@User channel:#channel limit:10 since:7d")
@commands.has_permissions(administrator=True)
async def history(ctx, *, args: str = ""):
    if not db_manager.pool:
        await ctx.send("Database is not connected. Please try again later.")
        return

    # Extract optional parameters from message content
    user = ctx.message.mentions[0] if ctx.message.mentions else None
    channel = ctx.message.channel_mentions[0] if ctx.message.channel_mentions else ctx.channel

    limit_match = re.search(r'(?:\blimit\s*[:=]\s*)(\d+)', args, re.IGNORECASE)
    limit = int(limit_match.group(1)) if limit_match else 10
    limit = max(1, min(limit, 100))  # clamp 1..100

    since_match = re.search(r'(?:\bsince\s*[:=]\s*)(\d+\s*[mhd])', args, re.IGNORECASE)
    since = since_match.group(1).replace(" ", "") if since_match else None

    since_dt = _parse_duration_to_since(since) if since else None
    if since and since_dt is None:
        await ctx.send("Invalid timeframe. Use formats like 1h, 24h, 7d, or 30m.")
        return

    channel_id = channel.id if channel else None

    try:
        rows = await db_manager.get_messages(
            user_id=(user.id if user else None),
            channel_id=channel_id,
            limit=limit,
            since=since_dt,
        )

        if not rows:
            await ctx.send("No messages found for the given filters.")
            return

        # Format a concise plain-text response, keeping under Discord 2000-char limit
        lines = []
        for row in rows:
            ts = row.get('timestamp')
            ts_str = ts.strftime('%Y-%m-%d %H:%M:%S') + ' UTC' if isinstance(ts, datetime) else 'Unknown time'
            ch_name = row.get('channel_name') or f"#{row.get('channel_id')}"
            username = row.get('username') or str(row.get('user_id'))
            content = (row.get('content') or '').replace('\n', ' ')
            if len(content) > 180:
                content = content[:177] + '...'
            lines.append(f"{ts_str} | #{ch_name} | {username}: {content}")

        # Truncate to fit within limits
        out_lines = []
        total = 0
        for line in lines:
            if total + len(line) + 1 > 1900:
                break
            out_lines.append(line)
            total += len(line) + 1

        header_bits = []
        if user:
            header_bits.append(f"user=@{user.name}")
        if channel_id:
            header_bits.append(f"channel=#{getattr(channel, 'name', channel_id)}")
        if since_dt:
            header_bits.append(f"since={since}")
        header = "; ".join(header_bits) or "no filters"

        await ctx.send(f"Showing up to {len(out_lines)} messages ({header}):\n" + "\n".join(out_lines))
    except Exception as e:
        await ctx.send(f"Error fetching history: {e}")

@history.error
async def history_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need Administrator permission to use this command.")
    else:
        await ctx.send(f"Error: {error}")

# !summarize command: use AI to summarize messages by user and/or channel with limit/timeframe
@bot.command(name="summarize", help="Use AI to summarize messages from the database. Usage: !summarize [options]\nOptions: user:@User channel:#channel limit:50 since:7d")
@commands.has_permissions(administrator=True)
async def summarize(ctx, *, args: str = ""):
    if not db_manager.pool:
        await ctx.send("Database is not connected. Please try again later.")
        return

    # Extract optional parameters from message content
    user = ctx.message.mentions[0] if ctx.message.mentions else None
    channel = ctx.message.channel_mentions[0] if ctx.message.channel_mentions else ctx.channel

    limit_match = re.search(r'(?:\blimit\s*[:=]\s*)(\d+)', args, re.IGNORECASE)
    limit = int(limit_match.group(1)) if limit_match else 50
    limit = max(1, min(limit, 200))  # clamp 1..200

    since_match = re.search(r'(?:\bsince\s*[:=]\s*)(\d+\s*[mhd])', args, re.IGNORECASE)
    since = since_match.group(1).replace(" ", "") if since_match else None

    since_dt = _parse_duration_to_since(since) if since else None
    if since and since_dt is None:
        await ctx.send("Invalid timeframe. Use formats like 1h, 24h, 7d, or 30m.")
        return

    channel_id = channel.id if channel else None

    # Require at least one filter
    if not user and not channel_id and not since_dt:
        await ctx.send("Please specify at least one filter: user, channel, or timeframe.")
        return

    try:
        # Fetch messages from database
        rows = await db_manager.get_messages(
            user_id=(user.id if user else None),
            channel_id=channel_id,
            limit=limit,
            since=since_dt,
        )

        if not rows:
            await ctx.send("No messages found to summarize.")
            return

        # Generate summary using LLM
        user_filter = user.name if user else None
        channel_filter = channel.name if channel else None
        
        summary = await llm_service.summarize_messages(
            messages=rows,
            user_filter=user_filter,
            channel_filter=channel_filter
        )

        # Build response header
        header_bits = []
        if user:
            header_bits.append(f"@{user.name}")
        if channel_id:
            header_bits.append(f"#{channel_filter}")
        if since_dt:
            header_bits.append(f"last {since}")
        header = " | ".join(header_bits) or "no filters"

        # Create embed for better formatting
        embed = discord.Embed(
            title="📊 Message Summary",
            description=summary[:4000],  # Discord embed description limit
            color=discord.Color.blue(),
            timestamp=datetime.now(datetime.UTC)
        )
        embed.add_field(name="Filters", value=header, inline=False)
        embed.add_field(name="Messages Analyzed", value=str(len(rows)), inline=True)
        embed.set_footer(text="Generated using AI")

        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"Error generating summary: {e}")

@summarize.error
async def summarize_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need Administrator permission to use this command.")
    else:
        await ctx.send(f"Error: {error}")

# !ask command: answer a question using messages filtered by user/channel/timeframe
@bot.command(name="ask", help="Ask a question about messages. Usage: !ask [options] question: <your question>\nOptions: user:@User channel:#channel limit:50 since:7d")
@commands.has_permissions(administrator=True)
async def ask(ctx, *, args: str = ""):
    if not db_manager.pool:
        await ctx.send("Database is not connected. Please try again later.")
        return

    # Extract optional parameters from message content
    user = ctx.message.mentions[0] if ctx.message.mentions else None
    channel = ctx.message.channel_mentions[0] if ctx.message.channel_mentions else ctx.channel

    limit_match = re.search(r'(?:\blimit\s*[:=]\s*)(\d+)', args, re.IGNORECASE)
    limit = int(limit_match.group(1)) if limit_match else 50
    limit = max(1, min(limit, 200))  # clamp 1..200

    since_match = re.search(r'(?:\bsince\s*[:=]\s*)(\d+\s*[mhd])', args, re.IGNORECASE)
    since = since_match.group(1).replace(" ", "") if since_match else None

    since_dt = _parse_duration_to_since(since) if since else None
    if since and since_dt is None:
        await ctx.send("Invalid timeframe. Use formats like 1h, 24h, 7d, or 30m.")
        return

    channel_id = channel.id if channel else None

    # Extract the question: prefer explicit question: <text>; otherwise use remaining text
    question_match = re.search(r'\bquestion\s*[:=]\s*(.+)', args, re.IGNORECASE)
    if question_match:
        question_text = question_match.group(1).strip()
    else:
        # Remove known flags and mentions to leave the question residue
        residue = args
        if limit_match:
            residue = residue.replace(limit_match.group(0), "")
        if since_match:
            residue = residue.replace(since_match.group(0), "")
        # Remove mention tokens like <@123>, <#456>, <@!789>
        residue = re.sub(r'<[@#][!&]?\d+>', '', residue)
        # Remove common keywords
        residue = re.sub(r'\b(user|channel|limit|since|question)\b\s*[:=]?', '', residue, flags=re.IGNORECASE)
        question_text = residue.strip()

    if not question_text:
        await ctx.send("Please provide a question. Example: !ask user:@Alice since:24h question: What did they talk about?")
        return

    # Require at least one filter to bound context
    if not user and not channel_id and not since_dt:
        await ctx.send("Please specify at least one filter: user, channel, or timeframe.")
        return

    try:
        # Fetch messages from database
        rows = await db_manager.get_messages(
            user_id=(user.id if user else None),
            channel_id=channel_id,
            limit=limit,
            since=since_dt,
        )

        if not rows:
            await ctx.send("No messages found to answer from.")
            return

        # Answer using LLM
        user_filter = user.name if user else None
        channel_filter = channel.name if channel else None

        answer = await llm_service.ask_question(
            messages=rows,
            question=question_text,
            user_filter=user_filter,
            channel_filter=channel_filter,
        )

        # Build response header
        header_bits = []
        if user:
            header_bits.append(f"@{user.name}")
        if channel_id:
            header_bits.append(f"#{channel_filter}")
        if since_dt:
            header_bits.append(f"last {since}")
        header = " | ".join(header_bits) or "no filters"

        # Create embed for better formatting
        embed = discord.Embed(
            title="📚 Answer",
            description=answer[:4000],  # Discord embed description limit
            color=discord.Color.green(),
            timestamp=datetime.now(UTC)
        )
        embed.add_field(name="Filters", value=header, inline=False)
        embed.add_field(name="Messages Analyzed", value=str(len(rows)), inline=True)
        embed.set_footer(text="Answered using AI from recent messages")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Error generating answer: {e}")

@ask.error
async def ask_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need Administrator permission to use this command.")
    else:
        await ctx.send(f"Error: {error}")

@bot.event
async def on_message(message):
    """Called whenever a message is sent in a channel the bot can see"""
    # Don't respond to the bot's own messages
    if message.author == bot.user:
        return

    # Collect comprehensive message metadata
    print("\n" + "="*80)
    print("MESSAGE RECEIVED:")
    print("="*80)

    # Server/Guild Information
    if message.guild:
        print(f"🏠 Server: {message.guild.name} (ID: {message.guild.id})")
        print(f"👑 Server Owner: {message.guild.owner.name if message.guild.owner else 'Unknown'}")
        print(f"👥 Member Count: {message.guild.member_count}")
    else:
        print("📩 Direct Message")

    # Channel Information
    print(f"📺 Channel: #{message.channel.name} (ID: {message.channel.id})")
    print(f"🏷️  Channel Type: {message.channel.type}")
    if hasattr(message.channel, 'category') and message.channel.category:
        print(f"📁 Category: {message.channel.category.name}")
    if hasattr(message.channel, 'topic') and message.channel.topic:
        print(f"📝 Channel Topic: {message.channel.topic}")

    # User Information
    print(f"👤 Author: {message.author.name}#{message.author.discriminator} (ID: {message.author.id})")
    print(f"🎭 Display Name: {message.author.display_name}")
    print(f"🤖 Is Bot: {message.author.bot}")
    if message.guild and message.author in message.guild.members:
        member = message.guild.get_member(message.author.id)
        if member:
            print(f"📅 Joined Server: {member.joined_at.strftime('%Y-%m-%d %H:%M:%S') if member.joined_at else 'Unknown'}")
            if member.roles and len(member.roles) > 1:  # Exclude @everyone role
                roles = [role.name for role in member.roles[1:]]  # Skip @everyone
                print(f"🎖️  Roles: {', '.join(roles)}")

    # Message Information
    print(f"💬 Content: {message.content}")
    print(f"🕐 Timestamp: {message.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"📧 Message ID: {message.id}")

    # Attachments
    if message.attachments:
        print(f"📎 Attachments ({len(message.attachments)}):")
        for i, attachment in enumerate(message.attachments, 1):
            print(f"   {i}. {attachment.filename} ({attachment.size} bytes) - {attachment.url}")

    # Embeds
    if message.embeds:
        print(f"🔗 Embeds ({len(message.embeds)}):")
        for i, embed in enumerate(message.embeds, 1):
            print(f"   {i}. Title: {embed.title or 'No title'}")
            if embed.description:
                print(f"      Description: {embed.description[:100]}{'...' if len(embed.description) > 100 else ''}")

    # Mentions
    if message.mentions:
        mentioned_users = [f"{user.name}#{user.discriminator}" for user in message.mentions]
        print(f"👥 Mentions Users: {', '.join(mentioned_users)}")

    if message.role_mentions:
        mentioned_roles = [role.name for role in message.role_mentions]
        print(f"🎖️  Mentions Roles: {', '.join(mentioned_roles)}")

    if message.channel_mentions:
        mentioned_channels = [f"#{channel.name}" for channel in message.channel_mentions]
        print(f"📺 Mentions Channels: {', '.join(mentioned_channels)}")

    # Reactions (if any)
    if message.reactions:
        print(f"😀 Reactions ({len(message.reactions)}):")
        for reaction in message.reactions:
            print(f"   {reaction.emoji}: {reaction.count}")

    # Message flags/properties
    flags = []
    if message.pinned:
        flags.append("📌 Pinned")
    if message.tts:
        flags.append("🔊 Text-to-Speech")
    if message.mention_everyone:
        flags.append("📢 @everyone/@here")
    if hasattr(message, 'reference') and message.reference:
        flags.append("↩️ Reply")
    if flags:
        print(f"🏷️  Flags: {', '.join(flags)}")

    print("="*80)

    # Store data in database (text-only, minimal)
    if db_manager.pool:  # Only if database is connected
        try:
            # Only store plain text messages (skip empty content)
            if not message.content:
                return

            # Ensure channel and user rows exist (insert-only)
            await db_manager.ensure_channel_exists(
                channel_id=message.channel.id,
                server_id=message.guild.id if message.guild else None,
                name=message.channel.name,
            )
            await db_manager.ensure_user_exists(
                user_id=message.author.id,
                username=message.author.name,
            )

            # Prepare minimal message data
            message_data = {
                'message_id': message.id,
                'channel_id': message.channel.id,
                'user_id': message.author.id,
                'content': message.content,
                'timestamp': message.created_at.replace(tzinfo=None),
            }

            # Store message (insert-only)
            await db_manager.insert_message(message_data)

            # Get updated count
            total_count = await db_manager.get_message_count()
            print(f"✅ Message stored (text only). Total messages in DB: {total_count}")

        except Exception as e:
            print(f"❌ Error storing message in database: {e}")

    # Let the commands extension process prefix commands like !history
    await bot.process_commands(message)

# Start the bot
if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')

    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables.")
        print("Please check your .env file.")
    else:
        print("Starting bot...")
        bot.run(token)
