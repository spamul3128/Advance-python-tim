"""
LLM operations for message summarization using OpenAI API
"""
import os
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    """Service for LLM operations using OpenAI"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("⚠️ OPENAI_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)
    
    async def summarize_messages(
        self, 
        messages: List[Dict],
        user_filter: Optional[str] = None,
        channel_filter: Optional[str] = None
    ) -> Optional[str]:
        """
        Summarize a list of messages using OpenAI GPT.
        
        Args:
            messages: List of message dictionaries from database
            user_filter: Username if filtering by user
            channel_filter: Channel name if filtering by channel
            
        Returns:
            Summary string or None if error
        """
        if not self.client:
            return "⚠️ LLM service not available (missing API key)"
        
        if not messages:
            return "No messages to summarize"
        
        # Format messages for the prompt
        formatted_messages = []
        for msg in messages:
            username = msg.get('username', 'Unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp')
            
            if timestamp:
                time_str = timestamp.strftime('%Y-%m-%d %H:%M')
            else:
                time_str = 'Unknown time'
            
            formatted_messages.append(f"[{time_str}] {username}: {content}")
        
        # Build context description
        context_parts = []
        if user_filter:
            context_parts.append(f"from user @{user_filter}")
        if channel_filter:
            context_parts.append(f"in channel #{channel_filter}")
        
        context = f" {' '.join(context_parts)}" if context_parts else ""
        
        # Create the prompt
        messages_text = "\n".join(formatted_messages)
        prompt = f"""Please provide a concise summary of the following Discord messages{context}.
Focus on:
1. Main topics discussed
2. Key decisions or conclusions
3. Any action items or questions raised
4. Overall tone/sentiment

Messages:
{messages_text}

Provide the summary in a clear, structured format suitable for Discord display."""

        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes Discord conversations concisely and clearly."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4096,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Error calling OpenAI API: {e}")
            return f"Error generating summary: {str(e)}"

    async def ask_question(
        self,
        messages: List[Dict],
        question: str,
        user_filter: Optional[str] = None,
        channel_filter: Optional[str] = None,
    ) -> Optional[str]:
        """
        Answer a user question using ONLY the provided Discord messages as context.

        Args:
            messages: List of message dictionaries from database
            question: The user's question to answer about the messages
            user_filter: Username if filtering by user
            channel_filter: Channel name if filtering by channel

        Returns:
            Answer string or error details
        """
        if not self.client:
            return "⚠️ LLM service not available (missing API key)"
        if not messages:
            return "No messages available to answer from"
        question = (question or "").strip()
        if not question:
            return "Please provide a question to answer"

        # Format messages for prompt (reuse style from summarize)
        formatted_messages = []
        for msg in messages:
            username = msg.get('username', 'Unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp')
            time_str = timestamp.strftime('%Y-%m-%d %H:%M') if timestamp else 'Unknown time'
            formatted_messages.append(f"[{time_str}] {username}: {content}")

        context_parts = []
        if user_filter:
            context_parts.append(f"from user @{user_filter}")
        if channel_filter:
            context_parts.append(f"in channel #{channel_filter}")
        context = f" {' '.join(context_parts)}" if context_parts else ""

        messages_text = "\n".join(formatted_messages)
        prompt = f"""You are a precise assistant that answers questions about Discord conversations.
You MUST answer using ONLY the information present in the provided messages{context}. If the answer cannot be determined from the messages, say so explicitly.
Be concise and cite specific messages or time ranges when helpful.

Question: {question}

Messages:
{messages_text}

Answer:"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You answer strictly from the given messages; do not invent facts beyond the context."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2048,
                temperature=0.4,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error calling OpenAI API for ask_question: {e}")
            return f"Error generating answer: {str(e)}"


# Global LLM service instance
llm_service = LLMService()
