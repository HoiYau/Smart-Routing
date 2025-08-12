# main.py — Streamlit App for Smart Routing
import streamlit as st
import methods
import uuid
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Smart Routing App", layout="wide")
page = st.sidebar.radio("Navigate", ["Lead Scoring", "Available Rooms Dashboard", "Agent Load & Status"])

# Lead Scoring Page
if page == "Lead Scoring":
    st.title("\U0001F4E1 Smart Routing - Lead Intake")
    with st.form("lead_form"):
        lead_id = str(uuid.uuid4())
        budget = st.number_input("Your Budget (RM)", min_value=0, step=0, format="%d")
        move_in_date = st.date_input("Desired Move-in Date", min_value=datetime.now().date())
        location = st.selectbox("Location", ["Setapak", "Subang", "Wangsa Maju"])
        contact_provided = st.checkbox("Contact Provided")
        bedroom_type = st.selectbox("Room Type", ["Master Room", "Medium Room", "Small Room"])
        user_type = st.selectbox("I am a...", ["Employee", "Student"])
        message = st.text_area("Message")
        reset_after_submit = st.checkbox("Reset agent loads after each lead (for testing)")
        submitted = st.form_submit_button("Process Lead")

    if submitted:
        score = methods.calculate_alps_score(budget, move_in_date, location, contact_provided, bedroom_type, user_type)
        agent = methods.assign_lead_by_score(score)

        # Determine queue label based on score
        if score >= 90:
            queue = "Top Agent Queue"
        elif score >= 80:
            queue = "Shared Tier Queue (Top/Senior)"
        else:
            queue = "Cold Tier Queue (Senior/Junior)"

        st.success("Lead Processed")
        st.write(f"**Lead ID:** {lead_id}")
        st.write(f"**ALPS Score:** {score}/100")
        st.write(f"**Assigned Queue:** {queue}")
        st.write(f"**Assigned Agent:** {agent if agent else 'None Available'}")

        if reset_after_submit:
            for a in methods.AGENT_POOL:
                methods.reset_agent_load(a["name"])
            methods.SHARED_TIER_QUOTA.update({
                "Top": 4,
                "Senior": 3,
                "Junior": 2
            })
            st.info("Agent loads and tier quotas have been reset.")

# Available Rooms Dashboard
elif page == "Available Rooms Dashboard":
    st.title("\U0001F3D8️ Property Availability Dashboard")
    for prop in methods.properties:
        st.header(f"{prop['name']} — {prop['location']}")
        for unit in prop["units"]:
            with st.expander(f"{unit['unit_id']}"):
                for idx, room in enumerate(unit["rooms"]):
                    status = "✅ Available" if not room["occupied"] else "❌ Rented"
                    st.markdown(f"**Room {idx+1}**: {room['type']} - RM{room['price']} — {status}")

# Agent Load & Status Page
elif page == "Agent Load & Status":
    st.title("\U0001F465 Agent Load & Status Overview")
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

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            **{agent['name']}**  
            Role: {agent['role']} | Tier: {agent['tier']}  
            Load: {agent['load']}/{agent['max_load']}  
            Status: <span class='{color}'>{agent['status']}</span>
            """, unsafe_allow_html=True)
        with col2:
            if st.button(f"Reset {agent['name']}"):
                methods.reset_agent_load(agent['name'])
                st.session_state["just_reset"] = True

        st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("Reset ALL agents"):
        for a in methods.AGENT_POOL:
            methods.reset_agent_load(a["name"])
        st.success("All agents have been reset.")
