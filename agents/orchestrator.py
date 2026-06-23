from typing import Dict, Any, List
from .base_agent import BaseAgent
import json

class OrchestratorAgent(BaseAgent):
    """Coordinates all agents to fulfill user requests"""
    
    def __init__(self):
        super().__init__(name="Orchestrator")
        self.task_history = []
    
    def plan(self, user_query: str) -> Dict[str, Any]:
        """Break down user query into a plan"""
        
        prompt = f"""
        You are a business growth orchestrator. Given a user query, create a detailed plan.
        
        User Query: {user_query}
        
        Return a JSON with:
        1. primary_goal: The main objective
        2. required_data: What data needs to be analyzed
        3. output_type: What to produce (insights, content, strategy, or all)
        4. tasks: List of tasks for other agents
        5. brand_voice: Recommended brand voice
        
        Example format:
        {{
            "primary_goal": "Understand top products and create marketing campaign",
            "required_data": ["sales_by_product", "customer_demographics"],
            "output_type": "content",
            "tasks": [
                {{"agent": "data_query", "description": "Get top 5 products by revenue"}},
                {{"agent": "marketing", "description": "Create email campaign for top product"}}
            ],
            "brand_voice": "professional"
        }}
        """
        
        response = self.call_llm(prompt)
        plan = self.parse_json_response(response)
        self.task_history.append({"query": user_query, "plan": plan})
        
        return plan
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process orchestration tasks"""
        query = input_data.get("query", "")
        if not query:
            return {"error": "No query provided"}
        
        return self.plan(query)