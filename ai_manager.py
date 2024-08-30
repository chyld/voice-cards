from openai import OpenAI
from config_manager import config
import asyncio

class AIManager:
    def __init__(self):
        self.client = OpenAI(api_key=config.api_key)

    async def process_with_chatgpt(self, transcribed_text, expected_answer):
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that interprets spoken math answers. The user will provide a transcribed text of a spoken answer to a multiplication problem. Your task is to interpret this text and determine if it matches the expected answer. If it does, respond with just the number. If the user says 'stop', 'quit', or 'exit', respond with 'EXIT'. Otherwise, respond with 'UNCLEAR'."},
                {"role": "user", "content": f"The transcribed answer is '{transcribed_text}'. The expected answer is {expected_answer}. What did the user say?"}
            ]
        )
        return response.choices[0].message.content.strip()

ai_manager = AIManager()