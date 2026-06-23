from typing import Dict, Any, List
from .base_agent import BaseAgent
import json

class TrendAnalysisAgent(BaseAgent):
    """Analyzes business data to identify trends and predict future patterns."""
    
    def __init__(self):
        super().__init__(name="TrendAnalysisAgent")
        
    def analyze_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Gemini to identify trends in the provided business data.
        Returns trend predictions and actionable insights.
        """
        prompt = f"""
        You are a seasoned data analyst specializing in small business trends.
        Please analyze the following business data and identify key trends.
        
        Business Data:
        {json.dumps(data, indent=2)}
        
        Return a JSON with:
        1. "identified_trends": List of strings describing current trends
        2. "predictions": List of strings predicting future patterns
        3. "recommendations": List of actionable recommendations based on these trends
        """
        response = self.call_llm(prompt)
        return self.parse_json_response(response)
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implementation of the base abstract process method."""
        data = input_data.get("data", {})
        if not data:
            return {"error": "No data provided for trend analysis"}
        return self.analyze_trends(data)
