import streamlit as st
import requests
from datetime import datetime, date

# --- CONFIG ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

STAGES = ["Prospect", "Contacted", "Meeting Booked", "Proposal Sent", "Won", "Lost"]

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
    return r.status_code == 201

def update_lead_stage(lead_id, new_stage):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}",
        headers=HEADERS,
        json={"stage": new_stage, "updated_at": datetime.now().isoformat()}
    )
    return r.status_code == 204

def delete_lead(lead_id):
    r = requests.delete(
        f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}",
        headers=HEADERS
    )
    return r.status_code == 204

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
    return r.status_code == 201

def complete_task(task_id):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/tasks?id=eq.{task_id}",
        headers=HEADERS,
        json={"status": "Done"}
    )
    return r.status_code == 204

def delete_task(task_id):
    r = requests.delete(
        f"{SUPABASE_URL}/rest/v1/tasks?id=eq.{task_id}",
        headers=HEADERS
    )
    return r.status_code == 204

# --- PAGE ---
st.set_page_config(page_title="Pitchcraft CRM", layout="wide")
st.title("📋 Pitchcraft CRM")

tab1, tab2 = st.tabs(["Pipeline", "Add Lead"])

# --- TAB 1: PIPELINE ---
with tab1:
    leads = get_leads()

    if not leads:
        st.info("No leads yet. Add one in the 'Add Lead' tab.")
    else:
        cols = st.columns(len(STAGES))
        for col, stage in zip(cols, STAGES):
            stage_leads = [l for l in leads if l["stage"] == stage]
            with col:
                st.markdown(f"### {stage}")
                st.caption(f"{len(stage_leads)} lead{'s' if len(stage_leads) != 1 else ''}")
                for lead in stage_leads:
                    with st.expander(f"🏢 {lead['company_name']}"):
                        if lead.get("contact_name"):
                            st.write(f"👤 {lead['contact_name']}")
                        if lead.get("contact_email"):
                            st.write(f"✉️ {lead['contact_email']}")
                        if lead.get("source"):
                            st.write(f"📌 Source: {lead['source']}")
                        if lead.get("notes"):
                            st.write(f"📝 {lead['notes']}")

                        # Move stage
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

                        # Tasks
                        st.markdown("**Follow-up Tasks**")
                        tasks = get_tasks(lead["id"])
                        for task in tasks:
                            done = task["status"] == "Done"
                            tcol1, tcol2, tcol3 = st.columns([3, 1, 1])
                            with tcol1:
                                st.write(f"{'~~' if done else ''}{task['title']}{'~~' if done else ''} — {task.get('due_date', 'No date')}")
                            with tcol2:
                                if not done:
                                    if st.button("✅", key=f"done_{task['id']}"):
                                        complete_task(task["id"])
                                        st.rerun()
                            with tcol3:
                                if st.button("🗑️", key=f"deltask_{task['id']}"):
                                    delete_task(task["id"])
                                    st.rerun()

                        # Add task
                        with st.form(key=f"task_form_{lead['id']}"):
                            task_title = st.text_input("New task")
                            task_due = st.date_input("Due date", value=date.today())
                            if st.form_submit_button("Add Task"):
                                if task_title:
                                    add_task(lead["id"], task_title, task_due)
                                    st.rerun()

                        # Delete lead
                        if st.button("🗑️ Delete Lead", key=f"dellead_{lead['id']}"):
                            delete_lead(lead["id"])
                            st.rerun()

# --- TAB 2: ADD LEAD ---
with tab2:
    st.subheader("Add a New Lead")
    with st.form("add_lead_form"):
        company_name = st.text_input("Company Name *")
        contact_name = st.text_input("Contact Name")
        contact_email = st.text_input("Contact Email")
        source = st.text_input("Source (e.g. LinkedIn, Referral)")
        stage = st.selectbox("Initial Stage", STAGES)
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Lead")

        if submitted:
            if company_name:
                success = add_lead(company_name, contact_name, contact_email, source, stage, notes)
                if success:
                    st.success(f"✅ {company_name} added to pipeline!")
                else:
                    st.error("Something went wrong. Check your Supabase connection.")
            else:
                st.warning("Company name is required.")
