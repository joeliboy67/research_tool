import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from tavily import TavilyClient
import anthropic
from dotenv import load_dotenv

load_dotenv()

def load_companies():
    with open("companies.txt", "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def search_company_news(company_name):
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    results = client.search(
        query=f"{company_name} news developments 2025",
        search_depth="advanced",
        max_results=3
    )
    return results["results"]

def generate_digest(companies_data):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    content = ""
    for company, articles in companies_data.items():
        content += f"\n\n{company}:\n"
        for a in articles:
            content += f"- {a['title']}: {a.get('content', '')[:300]}\n"
    
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""Create a professional weekly digest email for a consultant.

For each company below, write a summary using clear bullet points covering:
- Most important recent development
- Any notable business news
- Anything relevant to a consultant approaching them

Do not use any asterisks or markdown formatting. Use plain text only.
Separate each company section with a divider line.

Date: {datetime.now().strftime("%d %B %Y")}

{content}"""
        }]
    )
    
    return message.content[0].text

def send_digest(digest_text):
    # Convert to HTML
    html_content = f"<html><body style='font-family: Arial, sans-serif;'>"
    
    for line in digest_text.split('\n'):
        if line.strip() and not line.startswith('-') and not line.startswith('=') and line.isupper():
            html_content += f"<h2 style='text-decoration: underline;'>{line}</h2>"
        elif line.startswith('-'):
            html_content += f"<p style='margin: 4px 0;'>{line}</p>"
        elif line.startswith('='):
            html_content += "<hr>"
        elif line.strip():
            html_content += f"<p><strong>{line}</strong></p>"
        else:
            html_content += "<br>"
    
    html_content += "</body></html>"
    
    message = Mail(
        from_email=os.getenv("SENDGRID_FROM_EMAIL"),
        to_emails=os.getenv("DIGEST_TO_EMAIL"),
        subject=f"Pitchcraft Weekly Digest — {datetime.now().strftime('%d %B %Y')}",
        html_content=html_content
    )
    
    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    sg.send(message)
    print("Digest sent successfully")
if __name__ == "__main__":
    print("Loading companies...")
    companies = load_companies()
    
    print(f"Searching news for {len(companies)} companies...")
    companies_data = {}
    for company in companies:
        print(f"  - {company}")
        companies_data[company] = search_company_news(company)
    
    print("Generating digest...")
    digest = generate_digest(companies_data)
    print(digest)
    
    print("Sending email...")
    send_digest(digest)