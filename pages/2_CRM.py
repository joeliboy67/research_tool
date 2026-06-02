import streamlit as st
import requests
from datetime import datetime, date

# --- CONFIG ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

STAGES = ["Prospect", "Contacted", "Meeting Booked", "Proposal Sent", "Won", "Lost"]

STAGE_COLOURS = {
    "Prospect": "#E8E8E8",
    "Contacted": "#D3E5FF",
    "Meeting Booked": "#FDECC8",
    "Proposal Sent": "#D1FAE5",
    "Won": "#BBF7D0",
    "Lost": "#FFE4E6"
}

STAGE_TEXT = {
    "Prospect": "#374151",
    "Contacted": "#1D4ED8",
    "Meeting Booked": "#92400E",
    "Proposal Sent": "#065F46",
    "Won": "#14532D",
    "Lost": "#9F1239"
}

# --- SUPABASE HELPERS ---
def get_leads():
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads?select=*&order=created_at.desc",
        headers=HEADERS
    )
    return r.json() if r.status_code == 200 else []

def add_lead(company_name, contact_name, contact_email, source, stage, notes):
    payload = {
        "company_name": company_name,
        "contact_name": contact_name,
        "contact_email": contact_email,
        "source": source,
        "stage": stage,
        "notes": notes
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/leads",
        headers=HEADERS,
        json=payload
    )
    return r.status_code in [200, 201]

def update_lead_stage(lead_id, new_stage):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}",
        headers=HEADERS,
        json={"stage": new_stage, "updated_at": datetime.now().isoformat()}
    )
    return r.status_code in [200, 204]

def delete_lead(lead_id):
    r = requests.delete(
        f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}",
        headers=HEADERS
    )
    return r.status_code in [200, 204]

def get_tasks(lead_id):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/tasks?lead_id=eq.{lead_id}&order=due_date.asc",
        headers=HEADERS
    )
    return r.json() if r.status_code == 200 else []

def add_task(lead_id, title, due_date):
    payload = {
        "lead_id": lead_id,
        "title": title,
        "due_date": due_date.isoformat() if due_date else None,
        "status": "Pending"
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/tasks",
        headers=HEADERS,
        json=payload
    )
    return r.status_code in [200, 201]

def complete_task(task_id):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/tasks?id=eq.{task_id}",
        headers=HEADERS,
        json={"status": "Done"}
    )
    return r.status_code in [200, 204]

def delete_task(task_id):
    r = requests.delete(
        f"{SUPABASE_URL}/rest/v1/tasks?id=eq.{task_id}",
        headers=HEADERS
    )
    return r.status_code in [200, 204]

# --- STYLES ---
def inject_styles():
    st.markdown("""
    <style>
        @import url('https:
