import os
import sys
# Force UTF-8 encoding for standard output (helps Windows terminals with emojis)
sys.stdout.reconfigure(encoding='utf-8')
import json
from typing import Dict, Any
from dotenv import load_dotenv
from agents.orchestrator import OrchestratorAgent
from agents.data_query_agent import DataQueryAgent
from agents.marketing_agent import MarketingAgent
from agents.critic_agent import CriticAgent
from agents.trend_analysis_agent import TrendAnalysisAgent
from agents.competitor_agent import CompetitorAgent
from agents.pricing_agent import PricingAgent

# Load environment variables
load_dotenv()

class SmallBusinessGrowthEngine:
    """Main orchestrator for the Small Business Growth Engine"""
    
    def __init__(self):
        # Initialize all agents
        self.orchestrator = OrchestratorAgent()
        self.data_agent = DataQueryAgent()
        self.marketing_agent = MarketingAgent()
        self.critic_agent = CriticAgent()
        self.trend_agent = TrendAnalysisAgent()
        self.competitor_agent = CompetitorAgent()
        self.pricing_agent = PricingAgent()
        
        # Session state
        self.session = {
            "history": [],
            "current_insights": None,
            "current_content": None
        }
        
        # Welcome message
        self.welcome = """
        🚀 Small Business Growth Engine
        ================================
        I help you understand your business data and create marketing content.
        
        Try asking:
        - "What are my top 5 products by revenue?"
        - "Show me sales trends for online channel"
        - "Create a marketing campaign for my best product"
        - "Who are my top customers and how can I market to them?"
        
        Enter 'exit' to quit.
        """
    
    def process_request(self, user_query: str) -> Dict[str, Any]:
        """Process a user request through the agent pipeline"""
        
        print(f"\n📝 Processing: {user_query}")
        print("-" * 40)
        
        try:
            # Step 1: Orchestrator creates a plan
            print("📋 Step 1: Planning...")
            plan = self.orchestrator.plan(user_query)
            print(f"   Plan: {plan.get('primary_goal', 'Unknown')}")
            
            # Step 2: Data agent analyzes
            print("📊 Step 2: Analyzing data...")
            insights = self.data_agent.analyze(user_query)
            self.session["current_insights"] = insights
            print(f"   Found {len(insights.get('analysis', {}))} data points")
            
            # Step 3: Marketing agent creates content (if needed)
            content = None
            if plan.get("output_type") in ["content", "all"]:
                print("✍️ Step 3: Generating content...")
                brand_voice = plan.get("brand_voice", "professional")
                content = self.marketing_agent.generate(insights, brand_voice)
                self.session["current_content"] = content
                print("   Content generated")
            
            # Step 4: Critic reviews everything
            print("🔍 Step 4: Reviewing quality...")
            review_result = self.critic_agent.review(
                content or insights,
                insights
            )
            print(f"   Quality score: {review_result.get('score', 0):.2%}")
            
            # Step 5: Compile results
            result = {
                "query": user_query,
                "plan": plan,
                "insights": insights,
                "content": content,
                "review": review_result,
                "status": "success"
            }
            
            # Store in session history
            self.session["history"].append({
                "query": user_query,
                "result": result
            })
            
            return result
            
        except Exception as e:
            return {
                "query": user_query,
                "status": "error",
                "error": str(e)
            }
    
    def display_results(self, result: Dict[str, Any]):
        """Display results in a user-friendly format"""
        if result.get("status") == "error":
            print(f"\n❌ Error: {result.get('error')}")
            return
        
        print("\n" + "=" * 60)
        print("📊 RESULTS")
        print("=" * 60)
        
        # Display insights
        if "insights" in result:
            insights = result["insights"]
            if insights and "insights" in insights:
                print("\n💡 KEY INSIGHTS:")
                print("-" * 40)
                summary = insights["insights"].get("summary", "") if isinstance(insights["insights"], dict) else ""
                if summary:
                    print(f"   {summary}")
                
                key_findings = insights["insights"].get("key_findings") if isinstance(insights["insights"], dict) else []
                if isinstance(key_findings, dict):
                    key_findings = list(key_findings.values())
                elif isinstance(key_findings, str):
                    key_findings = [key_findings]
                elif not isinstance(key_findings, list):
                    key_findings = []
                
                for i, finding in enumerate(key_findings[:3], 1):
                    print(f"   {i}. {finding}")
            
            # Show data summary
            if insights and "analysis" in insights:
                analysis = insights["analysis"]
                if isinstance(analysis, dict):
                    print("\n📈 DATA SUMMARY:")
                    print("-" * 40)
                    for key, value in analysis.items():
                        if isinstance(value, (int, float)):
                            print(f"   {key.replace('_', ' ').title()}: {value:,}")
        
        # Display content
        if "content" in result and result["content"]:
            content = result["content"]
            print("\n🎯 MARKETING CONTENT:")
            print("-" * 40)
            
            if "email_campaign" in content:
                email = content["email_campaign"]
                if isinstance(email, dict):
                    print(f"📧 Subject: {email.get('subject', 'N/A')}")
                    body = email.get('body') or email.get('content') or email.get('message') or ""
                    print(f"   Body: {body[:200]}...")
                elif isinstance(email, str):
                    print(f"📧 Email Campaign:")
                    print(f"   {email[:200]}...")
            
            if "social_posts" in content:
                print("\n📱 Social Posts:")
                posts = content["social_posts"]
                if isinstance(posts, dict):
                    posts_list = []
                    for k, v in posts.items():
                        if isinstance(v, dict):
                            v_text = v.get("text") or v.get("content") or v.get("post") or v.get("body") or v.get("message") or str(v)
                            posts_list.append({"platform": k, "text": v_text})
                        else:
                            posts_list.append({"platform": k, "text": str(v)})
                    posts = posts_list
                elif isinstance(posts, str):
                    posts = [posts]
                
                if isinstance(posts, (list, tuple)):
                    for i, post in enumerate(posts[:2], 1):
                        if isinstance(post, dict):
                            platform = post.get("platform", "")
                            text = post.get("text") or post.get("content") or post.get("post") or post.get("body") or post.get("message")
                            if not text:
                                string_vals = [v for v in post.values() if isinstance(v, str)]
                                text = string_vals[0] if string_vals else str(post)
                            
                            platform_str = f" [{platform}]" if platform else ""
                            print(f"   {i}.{platform_str} {text[:150]}...")
                        elif isinstance(post, str):
                            print(f"   {i}. {post[:150]}...")
                        else:
                            print(f"   {i}. {str(post)[:150]}...")
        
        # Display review
        if "review" in result:
            review = result["review"]
            print("\n✅ QUALITY REVIEW:")
            print("-" * 40)
            if isinstance(review, dict):
                print(f"   Score: {review.get('score', 0):.2%}")
                print(f"   Verified: {review.get('verified', False)}")
                
                strengths = review.get("strengths")
                if isinstance(strengths, dict):
                    strengths = list(strengths.values())
                elif isinstance(strengths, str):
                    strengths = [strengths]
                elif not isinstance(strengths, list):
                    strengths = []
                
                if strengths:
                    print(f"   Strengths: {'; '.join(strengths[:2])}")
        
        print("\n" + "=" * 60)
    
    def run(self):
        """Run the interactive CLI"""
        print(self.welcome)
        
        while True:
            try:
                # Get user input
                user_input = input("\n💬 You: ").strip()
                
                # Check for exit
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Goodbye! Happy growing!")
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Process the request
                result = self.process_request(user_input)
                
                # Display results
                self.display_results(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
    
    def process_batch(self, queries: list):
        """Process multiple queries in batch mode"""
        results = []
        for query in queries:
            print(f"\n{'='*60}")
            print(f"Processing: {query}")
            result = self.process_request(query)
            results.append(result)
            self.display_results(result)
        return results
    
    def get_session_summary(self) -> Dict:
        """Get summary of the current session"""
        return {
            "total_queries": len(self.session["history"]),
            "last_query": self.session["history"][-1] if self.session["history"] else None,
            "has_insights": self.session["current_insights"] is not None,
            "has_content": self.session["current_content"] is not None
        }

def main():
    """Main entry point"""
    # Check for API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY environment variable not set")
        print("Please set your API key:")
        print("  export GOOGLE_API_KEY='your-api-key-here'")
        print("  OR add it to a .env file")
        sys.exit(1)
    
    # Create the engine
    engine = SmallBusinessGrowthEngine()
    
    # Check if demo mode is requested via command line
    if "--demo" in sys.argv:
        print("\n📚 Running demo queries...")
        demo_queries = [
            "What are my top 3 products by revenue?",
            "Create a marketing email for my best performing product",
            "What's the average customer age and how can I target them?"
        ]
        results = engine.process_batch(demo_queries)
        print("\n📊 Session Summary:")
        print(json.dumps(engine.get_session_summary(), indent=2))
    else:
        # Run in interactive mode
        engine.run()

if __name__ == "__main__":
    main()