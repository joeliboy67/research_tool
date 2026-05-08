import sys
from search import search_company
from brief import generate_brief
from render import save_brief

def run(company_name):
    print(f"Researching {company_name}...")
    results = search_company(company_name)
    
    print("Generating brief...")
    brief = generate_brief(company_name, results)
    
    print("Saving document...")
    save_brief(company_name, brief)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py \"Company Name\"")
    else:
        company = " ".join(sys.argv[1:])
        run(company)