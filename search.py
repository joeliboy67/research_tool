import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

def search_company(company_name):
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    results = client.search(
        query=f"{company_name} company news financials key people 2025",
        search_depth="advanced",
        max_results=5
    )
    
    return results

if __name__ == "__main__":
    results = search_company("Rolls Royce Holdings")
    for r in results["results"]:
        print(r["title"])
        print(r["url"])
        print()