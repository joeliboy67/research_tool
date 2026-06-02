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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .main { background-color: #FFFFFF; }

        .crm-title {
            font-size: 2rem;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 0.25rem;
        }

        .crm-subtitle {
            font-size: 0.875rem;
            color: #9b9b9b;
            margin-bottom: 2rem;
        }

        .stage-header {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 0;
            border-bottom: 2px solid #F0F0F0;
            margin-bottom: 12px;
        }

        .stage-title {
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #6B7280;
        }

        .stage-count {
            font-size: 0.75rem;
            background: #F3F4F6;
            color: #6B7280;
            padding: 2px 8px;
            border-radius: 999px;
            font-weight: 500;
        }

        .lead-card {
            background: #FAFAFA;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 14px;
            margin-bottom: 10px;
        }

        .lead-card:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        .lead-company {
            font-size: 0.9rem;
            font-weight: 600;
            color: #111827;
            margin-bottom: 4px;
        }

        .lead-contact {
            font-size: 0.8rem;
            color: #6B7280;
            margin-bottom: 2px;
        }

        .lead-source {
            font-size: 0.75rem;
            color: #9CA3AF;
        }

        .stage-badge {
            display: inline-block;
            font-size: 0.7rem;
            font-weight: 500;
            padding: 2px 10px;
            border-radius: 999px;
            margin-top: 8px;
        }

        .task-row {
            font-size: 0.8rem;
            color: #374151;
            padding: 4px 0;
            border-bottom: 1px solid #F3F4F6;
        }

        .task-done {
            text-decoration: line-through;
            color: #9CA3AF;
        }

        .notion-divider {
            border: none;
            border-top: 1px solid #F0F0F0;
            margin: 12px 0;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- CARD HTML BUILDER ---
def build_card_html(lead):
    badge_bg = STAGE_COLOURS[lead["stage"]]
    badge_color = STAGE_TEXT[lead["stage"]]
    company = lead["company_name"]
    contact = lead.get("contact_name", "")
    email = lead.get("contact_email", "")
    source = lead.get("source", "")
    stage = lead["stage"]

    contact_line = f'<div class="lead-contact">&#128100; {contact}</div>' if contact else ""
    email_line = f'<div class="lead-contact">&#9993; {email}</div>' if email else ""
    source_line = f'<div class="lead-source">&#128204; {source}</div>' if source else ""
    badge = f'<span class="stage-badge" style="background:{badge_bg};color:{badge_color};">{stage}</span>'

    return (
        '<div class="lead-card">'
        f'<div class="lead-company">&#127970; {company}</div>'
        f'{contact_line}'
        f'{email_line}'
        f'{source_line}'
        f'{badge}'
        '</div>'
    )

# --- PAGE ---
st.set_page_config(page_title="Pitchcraft CRM", layout="wide")
inject_styles()

st.markdown('<div class="crm-title">&#128203; CRM Pipeline</div>', unsafe_allow_html=True)
st.markdown('<div class="crm-subtitle">Track leads, deals and follow-ups</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Pipeline", "Add Lead"])

# --- TAB 1: PIPELINE ---
with tab1:
    leads = get_leads()

    if not leads:
        st.markdown(
            '<div style="text-align:center;padding:60px 0;color:#9CA3AF;">'
            '<div style="font-size:2rem;margin-bottom:12px;">&#128235;</div>'
            '<div style="font-size:0.95rem;font-weight:500;">No leads yet</div>'
            '<div style="font-size:0.8rem;margin-top:4px;">Add your first lead using the tab above</div>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        cols = st.columns(len(STAGES))
        for col, stage in zip(cols, STAGES):
            stage_leads = [l for l in leads if l["stage"] == stage]
            with col:
                st.markdown(
                    '<div class="stage-header">'
                    f'<span class="stage-title">{stage}</span>'
                    f'<span class="stage-count">{len(stage_leads)}</span>'
                    '</div>',
                    unsafe_allow_html=True
                )

                for lead in stage_leads:
                    st.markdown(build_card_html(lead), unsafe_allow_html=True)

                    with st.expander("Manage", expanded=False):
                        if lead.get("notes"):
                            st.caption(lead["notes"])

                        new_stage = st.selectbox(
                            "Move to stage",
                            STAGES,
                            index=STAGES.index(lead["stage"]),
                            key=f"stage_{lead['id']}"
                        )
                        if new_stage != lead["stage"]:
                            if update_lead_stage(lead["id"], new_stage):
                                st.success("Stage updated!")
                                st.rerun()

                        st.markdown('<hr class="notion-divider">', unsafe_allow_html=True)
                        st.markdown("**Follow-up Tasks**")

                        tasks = get_tasks(lead["id"])
                        for task in tasks:
                            done = task["status"] == "Done"
                            tcol1, tcol2, tcol3 = st.columns([4, 1, 1])
                            with tcol1:
                                css_class = "task-row task-done" if done else "task-row"
                                due = task.get("due_date") or ""
                                st.markdown(
                                    f'<div class="{css_class}">{task["title"]} '
                                    f'<span style="color:#9CA3AF;font-size:0.7rem;">{due}</span></div>',
                                    unsafe_allow_html=True
                                )
                            with tcol2:
                                if not done:
                                    if st.button("✅", key=f"done_{task['id']}"):
                                        complete_task(task["id"])
                                        st.rerun()
                            with tcol3:
                                if st.button("🗑️", key=f"deltask_{task['id']}"):
                                    delete_task(task["id"])
                                    st.rerun()

                        with st.form(key=f"task_form_{lead['id']}"):
                            task_title = st.text_input("New task", placeholder="e.g. Send proposal")
                            task_due = st.date_input("Due date", value=date.today())
                            if st.form_submit_button("+ Add Task"):
                                if task_title:
                                    add_task(lead["id"], task_title, task_due)
                                    st.rerun()

                        st.markdown('<hr class="notion-divider">', unsafe_allow_html=True)
                        if st.button("🗑️ Delete Lead", key=f"dellead_{lead['id']}"):
                            delete_lead(lead["id"])
                            st.rerun()

# --- TAB 2: ADD LEAD ---
with tab2:
    st.markdown("### Add a New Lead")
    with st.form("add_lead_form"):
        company_name = st.text_input("Company Name *", placeholder="e.g. Acme Ltd")
        col1, col2 = st.columns(2)
        with col1:
            contact_name = st.text_input("Contact Name", placeholder="e.g. Jane Smith")
        with col2:
            contact_email = st.text_input("Contact Email", placeholder="e.g. jane@acme.com")
        col3, col4 = st.columns(2)
        with col3:
            source = st.text_input("Source", placeholder="e.g. LinkedIn, Referral")
        with col4:
            stage = st.selectbox("Initial Stage", STAGES)
        notes = st.text_area("Notes", placeholder="Any context about this lead...", height=100)
        submitted = st.form_submit_button("+ Add Lead", use_container_width=True)

        if submitted:
            if company_name:
                success = add_lead(company_name, contact_name, contact_email, source, stage, notes)
                if success:
                    st.success(f"{company_name} added to pipeline!")
                else:
                    st.error("Something went wrong. Check your Supabase connection.")
            else:
                st.warning("Company name is required.")
