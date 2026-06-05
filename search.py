import os
import os
from tavily import TavilyClient
from dotenv import load_dotenv
import concurrent.futures

load_dotenv()

def search_company(company_name):
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    queries = [
        f"{company_name} company news financials 2025",
        f"{company_name} CEO CMO president executives leadership team",
        f"{company_name} official website mission values marketing slogan brand",
        f"{company_name} CEO CMO keynote speech conference presentation 2024 2025",
        f"{company_name} CEO CMO interview podcast thought leadership strategy",
        f"{company_name} earnings call analyst questions transcript investor day",
        f"{company_name} investor presentation strategy priorities challenges",
        f"{company_name} CEO CMO LinkedIn articles posts",
        f"{company_name} challenges headwinds problems concerns annual report",
        f"{company_name} Cannes Lions FT conference SXSW Davos presentation",
    ]
    
    def run_search(query):
        try:
            return client.search(
                query=query,
                search_depth="advanced",
                max_results=3
            )["results"]
        except:
            return []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        all_results = list(executor.map(run_search, queries))
    
    combined = [r for results in all_results for r in results]
    
    # Remove duplicates by URL
    seen = set()
    unique_results = []
    for r in combined:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique_results.append(r)
    
    return {"results": unique_results}

if __name__ == "__main__":
    results = search_company("DEPT Agency")
    for r in results["results"]:
        print(r["title"])
        print(r["url"])
        print()
