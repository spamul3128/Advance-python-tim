"""
Utility functions for the Discord bot
"""
from datetime import datetime, timedelta, UTC
from typing import Optional


def parse_duration(duration_str: str) -> Optional[datetime]:
    """
    Parse duration strings like '1h', '24h', '7d', '30m' into a datetime from now.
    
    Args:
        duration_str: String representing duration (e.g., '1h', '7d', '30m')
        
    Returns:
        datetime object representing the time 'duration' ago from now, or None if invalid
    """
    try:
        s = duration_str.strip().lower()
        if not s:
            return None
            
        # Parse hours
        if s.endswith('h'):
            hours = int(s[:-1])
            return datetime.now(UTC) - timedelta(hours=hours)
            
        # Parse days
        if s.endswith('d'):
            days = int(s[:-1])
            return datetime.now(UTC) - timedelta(days=days)
            
        # Parse minutes
        if s.endswith('m'):
            minutes = int(s[:-1])
            return datetime.now(UTC) - timedelta(minutes=minutes)
            
        return None
    except (ValueError, AttributeError):
        return None


def format_message_for_display(row: dict, max_content_length: int = 180) -> str:
    """
    Format a database message row for display in Discord.
    
    Args:
        row: Dictionary containing message data from database
        max_content_length: Maximum length for message content before truncation
        
    Returns:
        Formatted string for display
    """
    ts = row.get('timestamp')
    ts_str = ts.strftime('%Y-%m-%d %H:%M:%S') + ' UTC' if isinstance(ts, datetime) else 'Unknown time'
    ch_name = row.get('channel_name') or f"#{row.get('channel_id')}"
    username = row.get('username') or str(row.get('user_id'))
    content = (row.get('content') or '').replace('\n', ' ')
    
    if len(content) > max_content_length:
        content = content[:max_content_length-3] + '...'
        
    return f"{ts_str} | #{ch_name} | {username}: {content}"


def truncate_for_discord(lines: list[str], max_chars: int = 1900) -> list[str]:
    """
    Truncate a list of lines to fit within Discord's character limit.
    
    Args:
        lines: List of strings to potentially truncate
        max_chars: Maximum total character count
        
    Returns:
        List of lines that fit within the limit
    """
    output_lines = []
    total_chars = 0
    
    for line in lines:
        if total_chars + len(line) + 1 > max_chars:
            break
        output_lines.append(line)
        total_chars += len(line) + 1
        
    return output_lines
