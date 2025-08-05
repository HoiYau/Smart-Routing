# methods.py — Smart Routing Logic & Scoring Utilities
from datetime import datetime

# -------------------------------
# Agent Profiles for Simulation
# -------------------------------
AGENT_POOL = [
    {"id": "Agent_S1", "name": "Emma Wilson", "role": "Property Specialist", "tier": "Top", "load": 0, "max_load": 5},
    {"id": "Agent_R1", "name": "David Chen", "role": "Sales Consultant", "tier": "Regular", "load": 0, "max_load": 5},
    {"id": "Agent_R2", "name": "Sarah Johnson", "role": "Customer Relations", "tier": "Regular", "load": 0, "max_load": 5},
    {"id": "Agent_R3", "name": "Alex Rodriguez", "role": "Leasing Agent", "tier": "Regular", "load": 0, "max_load": 5},
    {"id": "Agent_G1", "name": "Olivia Martinez", "role": "Junior Agent", "tier": "Junior", "load": 0, "max_load": 5},
]

# -------------------------------
# Tiered Assignment Logic
# -------------------------------
def assign_by_tier_priority(tiers):
    for tier in tiers:
        available = [a for a in AGENT_POOL if a["tier"].lower() == tier.lower() and a["load"] < a["max_load"]]
        if available:
            agent = sorted(available, key=lambda x: x["load"])[0]
            agent["load"] += 1
            update_agent_status(agent)
            return agent["name"]
    return None

def update_agent_status(agent):
    ratio = agent["load"] / agent["max_load"]
    if ratio >= 1.0:
        agent["status"] = "At Capacity"
    elif ratio >= 0.6:
        agent["status"] = "Busy"
    else:
        agent["status"] = "Available"

def get_all_agents():
    for agent in AGENT_POOL:
        update_agent_status(agent)
    return [
        {
            "name": agent["name"],
            "role": agent["role"],
            "tier": agent["tier"],
            "load": agent["load"],
            "max_load": agent["max_load"],
            "status": agent.get("status", "Available")
        }
        for agent in AGENT_POOL
    ]

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

def reset_agent_load(agent_name):
    for agent in AGENT_POOL:
        if agent["name"] == agent_name:
            agent["load"] = 0
            update_agent_status(agent)
            break

