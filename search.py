import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

def search_company(company_name):
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    # General company search
    general = client.search(
        query=f"{company_name} company news financials 2025",
        search_depth="advanced",
        max_results=5
    )
    
    # Targeted leadership search
    leadership = client.search(
        query=f"{company_name} CEO CMO president executives leadership team",
        search_depth="advanced",
        max_results=5
    )
    
    # Combine results
    combined = general["results"] + leadership["results"]
    
    # Remove duplicates by URL
    seen = set()
    unique_results = []
    for r in combined:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique_results.append(r)
    
    return {"results": unique_results}

if __name__ == "__main__":
    results = search_company("Rolls Royce Holdings")
    for r in results["results"]:
        print(r["title"])
        print(r["url"])
        print()