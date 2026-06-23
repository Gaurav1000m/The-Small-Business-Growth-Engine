from typing import Dict, Any, List
from .base_agent import BaseAgent
import json

class CompetitorAgent(BaseAgent):
    """Analyzes competitors based on the business context."""
    
    def __init__(self):
        super().__init__(name="CompetitorAgent")
        
    def analyze_competitors(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use web search (or simulate it via Gemini) to find competitor info
        and return competitive insights.
        """
        prompt = f"""
        You are a competitive intelligence expert.
        Analyze the competitive landscape for a business with the following profile.
        
        Business Data:
        {json.dumps(business_data, indent=2)}
        
        Based on industry knowledge and competitive context, return a JSON with:
        1. "top_competitors": List of generic or specific competitor archetypes
        2. "market_position": The business's inferred market position
        3. "competitive_advantages": Areas where this business can win
        4. "threats": Potential competitive threats
        """
        response = self.call_llm(prompt)
        return self.parse_json_response(response)
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implementation of the base abstract process method."""
        business_data = input_data.get("business_data", {})
        if not business_data:
            return {"error": "No business data provided for competitor analysis"}
        return self.analyze_competitors(business_data)
