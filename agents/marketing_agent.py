from typing import Dict, Any, List
from .base_agent import BaseAgent
import json
from datetime import datetime

class MarketingAgent(BaseAgent):
    """Generates marketing content based on business insights"""
    
    def __init__(self):
        super().__init__(name="MarketingAgent")
        self.content_history = []
    
    def generate(self, insights: Dict, brand_voice: str = "professional") -> Dict[str, Any]:
        """Generate marketing content based on insights"""
        
        prompt = f"""
        You are a marketing expert. Create content based on these business insights.
        
        Business Insights:
        {json.dumps(insights, indent=2)}
        
        Brand Voice: {brand_voice}
        
        Return a JSON with:
        1. email_campaign: Subject line, body, call-to-action
        2. social_posts: 3 social media posts (different platforms)
        3. ad_copy: 2 ad variations
        4. target_audience: Description of who to target
        5. recommended_actions: Next steps
        
        Make content specific, actionable, and personalized to the data.
        """
        
        response = self.call_llm(prompt)
        content = self.parse_json_response(response)
        
        # Store history
        self.content_history.append({
            "timestamp": datetime.now().isoformat(),
            "insights_summary": insights.get("summary", ""),
            "content": content
        })
        
        return content
    
    def _create_email(self, product: str, audience: str, insight: str) -> Dict:
        """Create a targeted email"""
        prompt = f"""
        Create a marketing email for {product}.
        Target audience: {audience}
        Key insight: {insight}
        
        Return as JSON with subject, body, and cta.
        """
        return self.parse_json_response(self.call_llm(prompt))
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process marketing content generation"""
        insights = input_data.get("insights", {})
        brand_voice = input_data.get("brand_voice", "professional")
        
        if not insights:
            return {"error": "No insights provided"}
        
        return self.generate(insights, brand_voice)