# main.py — Streamlit UI using methods.py
import streamlit as st
import uuid
from datetime import datetime
import methods  # make sure methods.py is in the same directory

# -------------------------------
# Streamlit UI - Page Control
# -------------------------------
st.set_page_config(page_title="Smart Routing App", layout="wide")
page = st.sidebar.radio("Navigate", ["Lead Scoring", "Available Rooms Dashboard"])

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
        queue = methods.route(score)
        agent = methods.assign(queue)

        st.success("Lead Processed")
        st.write(f"**Lead ID:** {lead_id}")
        st.write(f"**ALPS Score:** {score}/100")
        st.write(f"**Assigned Queue:** {queue}")
        st.write(f"**Assigned Agent:** {agent if agent else 'None Available'}")

elif page == "Available Rooms Dashboard":
    st.title("🏘️ Property Availability Dashboard")
    for prop in methods.properties:
        st.header(f"{prop['name']} — {prop['location']}")
        for unit in prop["units"]:
            with st.expander(f"{unit['unit_id']}"):
                for idx, room in enumerate(unit["rooms"]):
                    status = "✅ Available" if not room["occupied"] else "❌ Rented"
                    st.markdown(f"**Room {idx+1}**: {room['type']} - RM{room['price']} — {status}")
