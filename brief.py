import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You are a business research assistant helping a consultant prepare for prospect meetings.
Given raw research data about a company, produce a structured pitch brief.

Always output in this exact structure:

1. COMPANY OVERVIEW
A 3-4 sentence summary of what the company does.

2. RECENT NEWS & DEVELOPMENTS
Bullet points covering the last 12 months.

3. KEY PEOPLE
Name and title of important figures, with any relevant context.

4. LIKELY PAIN POINTS
What challenges is this company probably facing right now?

5. CONVERSATION HOOKS
2-3 tailored talking points the consultant can use to open a conversation.

6. OPEN QUESTIONS
Things worth asking in the meeting.

Be concise. If data is missing for a section, say so briefly.
"""

def generate_brief(company_name, search_results):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    raw_data = ""
    for result in search_results["results"]:
        raw_data += f"Title: {result['title']}\n"
        raw_data += f"URL: {result['url']}\n"
        raw_data += f"Content: {result.get('content', '')}\n\n"
    
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Company: {company_name}\n\nResearch data:\n{raw_data}"
            }
        ]
    )
    
    return message.content[0].text

if __name__ == "__main__":
    from search import search_company
    results = search_company("Rolls Royce Holdings")
    brief = generate_brief("Rolls Royce Holdings", results)
    print(brief)