from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import json
import os
import time
import google.generativeai as genai

class BaseAgent(ABC):
    """Base class for all agents with common functionality"""
    
    def __init__(self, name: str, model: str = "gemini-3.1-flash-lite"):
        self.name = name
        self.model_name = model
        self.memory = []
        
        # Configure Gemini
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name=model)
        self.chat = None
    
    def start_chat(self):
        """Initialize a chat session"""
        self.chat = self.model.start_chat(history=[])
        return self.chat
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output - to be implemented by child classes"""
        pass
    
    def call_llm(self, prompt: str) -> str:
        """Call the LLM with a prompt"""
        if not self.chat:
            self.start_chat()
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.chat.send_message(prompt)
                return response.text
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    print(f"\n   [Rate limit reached, waiting 60s before retry {attempt+1}/{max_retries}]")
                    time.sleep(60)
                else:
                    raise e
    
    def call_llm_with_context(self, prompt: str, context: list) -> str:
        """Call LLM with conversation context"""
        if not self.chat:
            self.start_chat()
        
        # Add context to memory
        for msg in context:
            self.chat.history.append(msg)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.chat.send_message(prompt)
                return response.text
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    print(f"\n   [Rate limit reached, waiting 60s before retry {attempt+1}/{max_retries}]")
                    time.sleep(60)
                else:
                    raise e
    
    def parse_json_response(self, response: str) -> Dict:
        """Parse JSON from LLM response"""
        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse JSON response: {e}")
            return {"error": "Failed to parse response", "raw": response}