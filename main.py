# Append this to your `main.py`
import streamlit as st
import methods
import uuid
from datetime import datetime

# Add new page in sidebar
st.set_page_config(page_title="Smart Routing App", layout="wide")
page = st.sidebar.radio("Navigate", ["Lead Scoring", "Available Rooms Dashboard", "Agent Load & Status"])

# Lead Scoring Page
if page == "Lead Scoring":
    st.title("📡 Smart Routing - Lead Intake")
    with st.form("lead_form"):
        lead_id = str(uuid.uuid4())
        budget = st.number_input("Your Budget (RM)", min_value=0, step=0, format="%d")
        move_in_date = st.date_input("Desired Move-in Date", min_value=datetime.now().date())
        location = st.selectbox("Location", ["Setapak", "Subang", "Wangsa Maju"])
        contact_provided = st.checkbox("Contact Provided")
        bedroom_type = st.selectbox("Room Type", ["Master Room", "Medium Room", "Small Room"])
        user_type = st.selectbox("I am a...", ["Employee", "Student"])
        message = st.text_area("Message")
        submitted = st.form_submit_button("Process Lead")

    if submitted:
        score = methods.calculate_alps_score(budget, move_in_date, location, contact_provided, bedroom_type, user_type)

        # Smart agent assignment simulation
        if score >= 70:
            agent = methods.assign_highest_tier()
            queue = "Senior Agent Queue"
        elif score >= 40:
            agent = methods.assign("Regular Agent Queue")
            queue = "Regular Agent Queue"
        else:
            agent = methods.assign("General Inquiry Queue")
            queue = "General Inquiry Queue"

        st.success("Lead Processed")
        st.write(f"**Lead ID:** {lead_id}")
        st.write(f"**ALPS Score:** {score}/100")
        st.write(f"**Assigned Queue:** {queue}")
        st.write(f"**Assigned Agent:** {agent if agent else 'None Available'}")

# Available Rooms Dashboard
elif page == "Available Rooms Dashboard":
    st.title("🏘️ Property Availability Dashboard")
    for prop in methods.properties:
        st.header(f"{prop['name']} — {prop['location']}")
        for unit in prop["units"]:
            with st.expander(f"{unit['unit_id']}"):
                for idx, room in enumerate(unit["rooms"]):
                    status = "✅ Available" if not room["occupied"] else "❌ Rented"
                    st.markdown(f"**Room {idx+1}**: {room['type']} - RM{room['price']} — {status}")

# Agent Load & Status
elif page == "Agent Load & Status":
    st.title("👥 Agent Load & Status Overview")
    agents = methods.get_all_agents()

    st.markdown("""
        <style>
        .status-green { color: green; font-weight: bold; }
        .status-yellow { color: orange; font-weight: bold; }
        .status-red { color: red; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    st.write("### Agent Roster")
    for agent in agents:
        color = "status-green" if agent['status'] == "Available" else "status-yellow" if agent['status'] == "Busy" else "status-red"
        st.markdown(f"""
        **{agent['name']}**  
        Role: {agent['role']} | Tier: {agent['tier']}  
        Load: {agent['load']}/{agent['max_load']}  
        Status: <span class='{color}'>{agent['status']}</span>
        <hr>
        """, unsafe_allow_html=True)
