from typing import Dict, Any, List
from .base_agent import BaseAgent
import pandas as pd
import json

class DataQueryAgent(BaseAgent):
    """Analyzes business data and extracts insights"""
    
    def __init__(self, data_path: str = "data/sample_business_data.csv"):
        super().__init__(name="DataQueryAgent")
        self.data = pd.read_csv(data_path)
        self.insights_cache = {}
    
    def analyze(self, query: str) -> Dict[str, Any]:
        """Analyze data based on natural language query"""
        
        # First, use Gemini to understand what data analysis is needed
        understanding_prompt = f"""
        Given this business data with columns: {list(self.data.columns)}
        
        Sample data (first 5 rows):
        {self.data.head().to_string()}
        
        User wants to know: {query}
        
        Return a JSON with:
        1. analysis_type: What kind of analysis (aggregation, filtering, trend, segmentation)
        2. filters: What filters to apply (product, city, channel, date range)
        3. metrics: What metrics to compute (total revenue, units sold, average price)
        4. group_by: How to group results
        5. sql_equivalent: Brief description of what to compute
        
        Example:
        {{
            "analysis_type": "aggregation",
            "filters": {{"channel": "Online"}},
            "metrics": ["total_revenue", "total_units"],
            "group_by": ["product"],
            "sql_equivalent": "Group by product, sum revenue and units for online sales"
        }}
        """
        
        analysis_plan = self.parse_json_response(self.call_llm(understanding_prompt))
        
        # Execute the analysis using pandas
        result = self._execute_analysis(analysis_plan)
        
        # Get insights from Gemini
        insight_prompt = f"""
        Based on this data analysis result:
        {json.dumps(result, indent=2)}
        
        Provide business insights. Return as JSON with:
        1. key_findings: List of top findings
        2. trends: Any trends observed
        3. recommendations: Actionable recommendations
        4. summary: Brief summary
        
        Keep it concise and business-focused.
        """
        
        insights = self.parse_json_response(self.call_llm(insight_prompt))
        
        # Cache the results
        cache_key = query[:50]  # Truncate for cache key
        self.insights_cache[cache_key] = {
            "query": query,
            "analysis": result,
            "insights": insights
        }
        
        return {
            "query": query,
            "analysis": result,
            "insights": insights
        }
    
    def _execute_analysis(self, plan: Dict) -> Dict:
        """Execute the pandas analysis based on the plan"""
        df = self.data.copy()
        
        # Apply filters
        if "filters" in plan:
            for key, value in plan["filters"].items():
                if key in df.columns:
                    df = df[df[key] == value]
        
        # Group by and aggregate
        group_by = plan.get("group_by", [])
        metrics = plan.get("metrics", [])
        
        if group_by and metrics:
            # Map metric names to pandas functions
            agg_dict = {}
            for metric in metrics:
                if "revenue" in metric:
                    agg_dict["revenue"] = "sum"
                elif "units" in metric:
                    agg_dict["units_sold"] = "sum"
                elif "average" in metric or "avg" in metric:
                    agg_dict["revenue"] = "mean"
            
            if agg_dict:
                result_df = df.groupby(group_by).agg(agg_dict).reset_index()
                result = result_df.to_dict(orient="records")
            else:
                result = df.groupby(group_by).size().reset_index(name="count").to_dict(orient="records")
        else:
            # Summary statistics
            result = {
                "total_revenue": float(df["revenue"].sum()),
                "total_units": int(df["units_sold"].sum()),
                "avg_order_value": float(df["revenue"].mean()),
                "unique_products": int(df["product"].nunique()),
                "record_count": len(df)
            }
        
        return result
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data query"""
        query = input_data.get("query", "")
        if not query:
            return {"error": "No query provided"}
        
        return self.analyze(query)