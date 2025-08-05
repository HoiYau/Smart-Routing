# methods.py — Smart Routing Logic & Scoring Utilities
import itertools
from datetime import datetime

# -------------------------------
# Agent Setup & Routing Logic
# -------------------------------
AGENTS = {
    "Senior Agent Queue": ["Agent_S1", "Agent_S2"],
    "Regular Agent Queue": ["Agent_R1", "Agent_R2", "Agent_R3"],
    "General Inquiry Queue": ["Agent_G1", "Agent_G2"]
}
agent_status = {aid: {"status": "online", "active": 0, "max": 5} for q in AGENTS.values() for aid in q}
agent_cycles = {q: itertools.cycle(AGENTS[q]) for q in AGENTS}

def route(score):
    return "Senior Agent Queue" if score >= 70 else "Regular Agent Queue" if score >= 40 else "General Inquiry Queue"

def assign(queue):
    for _ in range(len(AGENTS[queue])):
        aid = next(agent_cycles[queue])
        a = agent_status[aid]
        if a["status"] == "online" and a["active"] < a["max"]:
            a["active"] += 1
            return aid
    return None

# -------------------------------
# Static Property & Room Data
# -------------------------------
properties = [
    {"name": "The Grand Subang (SS15)", "location": "Subang", "units": [
        {"unit_id": "Unit-1", "rooms": [
            {"type": "Master Room", "price": 900, "occupied": False},
            {"type": "Master Room", "price": 1050, "occupied": False},
            {"type": "Small Room", "price": 400, "occupied": True},
        ]},
        {"unit_id": "Unit-2", "rooms": [
            {"type": "Master Room", "price": 1200, "occupied": True},
            {"type": "Medium Room", "price": 700, "occupied": False},
        ]},
        {"unit_id": "Unit-3", "rooms": [
            {"type": "Medium Room", "price": 850, "occupied": False},
            {"type": "Small Room", "price": 400, "occupied": False},
        ]},
        {"unit_id": "Unit-4", "rooms": [
            {"type": "Master Room", "price": 1000, "occupied": False},
            {"type": "Medium Room", "price": 800, "occupied": True},
        ]},
    ]},
    {"name": "MH2 Platinium", "location": "Setapak", "units": [
        {"unit_id": "Unit-1", "rooms": [
            {"type": "Master Room", "price": 1150, "occupied": False},
            {"type": "Medium Room", "price": 800, "occupied": True},
        ]},
        {"unit_id": "Unit-2", "rooms": [
            {"type": "Small Room", "price": 400, "occupied": True},
        ]},
        {"unit_id": "Unit-3", "rooms": [
            {"type": "Small Room", "price": 500, "occupied": True},
            {"type": "Medium Room", "price": 650, "occupied": False},
        ]},
        {"unit_id": "Unit-4", "rooms": [
            {"type": "Master Room", "price": 1000, "occupied": False},
            {"type": "Medium Room", "price": 700, "occupied": True},
        ]},
    ]},
    {"name": "The Hamilton", "location": "Wangsa Maju", "units": [
        {"unit_id": "Unit-1", "rooms": [
            {"type": "Master Room", "price": 1200, "occupied": False},
            {"type": "Small Room", "price": 400, "occupied": False},
        ]},
        {"unit_id": "Unit-2", "rooms": [
            {"type": "Medium Room", "price": 800, "occupied": False},
            {"type": "Medium Room", "price": 700, "occupied": False},
        ]},
        {"unit_id": "Unit-3", "rooms": [
            {"type": "Master Room", "price": 900, "occupied": True},
            {"type": "Small Room", "price": 400, "occupied": False},
        ]},
        {"unit_id": "Unit-4", "rooms": [
            {"type": "Medium Room", "price": 700, "occupied": True},
        ]},
    ]},
]

# -------------------------------
# ALPS Scoring Functions
# -------------------------------
def urgency_score(move_in):
    days = (move_in - datetime.now().date()).days
    return 10 if days <= 4 else 8 if days <= 15 else 6 if days <= 30 else 3

def count_room_type(location, room_type):
    return sum(
        1 for p in properties if p['location'] == location
        for u in p['units']
        for r in u['rooms']
        if not r['occupied'] and r['type'] == room_type
    )

def room_type_score(location, room_type):
    total = sum(
        1 for p in properties if p['location'] == location
        for u in p['units']
        for r in u['rooms'] if not r['occupied']
    )
    count = count_room_type(location, room_type)
    return round((count / total) * 10, 2) if total > 0 else 0

def user_type_bonus(user_type):
    return 2 if user_type == "Employee" else 0

def match_price_score(budget, location, room_type):
    matched = [r['price'] for p in properties if p['location'] == location for u in p['units'] for r in u['rooms'] if not r['occupied'] and r['type'] == room_type]
    if not matched:
        return 0
    closest = min(matched, key=lambda p: abs(p - budget))
    diff = abs(budget - closest) / closest
    return max(0, (1 - diff) * 20)

def calculate_alps_score(budget, move_in, location, contact, room_type, user_type):
    score = urgency_score(move_in) * 4
    score += match_price_score(budget, location, room_type)
    score += 5 if contact else 0
    score += 10 if location in ["Setapak", "Subang", "Wangsa Maju"] else 0
    score += room_type_score(location, room_type)
    score += user_type_bonus(user_type)
    return round(min(score, 100), 2)

# Extend methods.py with agent backend logic matching UI

# -------------------------------
# Agent Profiles (Matches Visuals)
# -------------------------------
agent_profiles = [
    {
        "id": "Agent_S1",
        "name": "Emma Wilson",
        "tier": "Top",
        "role": "Property Specialist",
        "load": 3,
        "max_load": 10,
        "status": "available"
    },
    {
        "id": "Agent_R1",
        "name": "David Chen",
        "tier": "Regular",
        "role": "Sales Consultant",
        "load": 7,
        "max_load": 10,
        "status": "busy"
    },
    {
        "id": "Agent_R2",
        "name": "Sarah Johnson",
        "tier": "Regular",
        "role": "Customer Relations",
        "load": 8,
        "max_load": 10,
        "status": "busy"
    },
    {
        "id": "Agent_R3",
        "name": "Alex Rodriguez",
        "tier": "Regular",
        "role": "Leasing Agent",
        "load": 10,
        "max_load": 10,
        "status": "full"
    },
    {
        "id": "Agent_G1",
        "name": "Olivia Martinez",
        "tier": "Junior",
        "role": "Junior Agent",
        "load": 2,
        "max_load": 5,
        "status": "available"
    }
]

# -------------------------------
# Agent API Accessors
# -------------------------------
def get_all_agents():
    return agent_profiles

def get_agent_by_id(agent_id):
    return next((a for a in agent_profiles if a["id"] == agent_id), None)

def assign_lead_to_agent(agent_id):
    agent = get_agent_by_id(agent_id)
    if not agent:
        return False, "Agent not found"
    if agent["load"] >= agent["max_load"]:
        return False, "Agent at full capacity"
    agent["load"] += 1
    update_agent_status(agent)
    return True, agent

def update_agent_status(agent):
    ratio = agent["load"] / agent["max_load"]
    if ratio >= 1.0:
        agent["status"] = "full"
    elif ratio >= 0.6:
        agent["status"] = "busy"
    else:
        agent["status"] = "available"

def get_all_agents():
    return [
        {"name": "Emma Wilson", "role": "Property Specialist", "tier": "Top", "load": 3, "max_load": 10, "status": "Available"},
        {"name": "David Chen", "role": "Sales Consultant", "tier": "Regular", "load": 7, "max_load": 10, "status": "Busy"},
        {"name": "Sarah Johnson", "role": "Customer Relations", "tier": "Regular", "load": 8, "max_load": 10, "status": "Busy"},
        {"name": "Alex Rodriguez", "role": "Leasing Agent", "tier": "Regular", "load": 10, "max_load": 10, "status": "At Capacity"},
        {"name": "Olivia Martinez", "role": "Junior Agent", "tier": "Junior", "load": 2, "max_load": 5, "status": "Available"},
    ]

