from typing import Dict, Any, List
from .base_agent import BaseAgent
import json

class CriticAgent(BaseAgent):
    """Reviews and validates work from other agents"""
    
    def __init__(self):
        super().__init__(name="CriticAgent")
    
    def review(self, content: Dict, insights: Dict) -> Dict[str, Any]:
        """Review content for quality, accuracy, and actionability"""
        
        prompt = f"""
        You are a quality reviewer. Review this marketing content against the business insights.
        
        Business Insights:
        {json.dumps(insights, indent=2)}
        
        Marketing Content:
        {json.dumps(content, indent=2)}
        
        Return a JSON with:
        1. verified: Boolean - is the content accurate and aligned with insights?
        2. score: Number - overall quality score (0-1)
        3. strengths: List of what's good
        4. improvements: List of suggestions
        5. summary: Brief review summary
        6. final_content: The content with improvements applied (if needed)
        """
        
        response = self.call_llm(prompt)
        review = self.parse_json_response(response)
        
        # If score is high, keep content; if low, suggest improvements
        if review.get("score", 0) < 0.7:
            # Request improved version
            improvement_prompt = f"""
            Based on this review:
            {json.dumps(review, indent=2)}
            
            Please provide an improved version of the content.
            Keep it concise and directly address the improvements.
            Return the final content in the same structure as the original.
            """
            
            improved = self.parse_json_response(self.call_llm(improvement_prompt))
            review["final_content"] = improved
        else:
            review["final_content"] = content
        
        return review
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process content review"""
        content = input_data.get("content", {})
        insights = input_data.get("insights", {})
        
        if not content:
            return {"error": "No content provided for review"}
        
        return self.review(content, insights)