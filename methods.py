# methods.py — Enhanced Smart Routing Logic with Tiered Load Balancing & Fairness
from datetime import datetime

# -------------------------------
# Agent Profiles (Simulation)
# -------------------------------
AGENT_POOL = [
    {"id": "Agent_S1", "name": "Emma Wilson", "role": "Property Specialist", "tier": "Top", "load": 0, "max_load": 5},
    {"id": "Agent_R1", "name": "David Chen", "role": "Sales Consultant", "tier": "Senior", "load": 0, "max_load": 5},
    {"id": "Agent_R2", "name": "Sarah Johnson", "role": "Customer Relations", "tier": "Senior", "load": 0, "max_load": 5},
    {"id": "Agent_G1", "name": "Alex Rodriguez", "role": "Leasing Agent", "tier": "Junior", "load": 0, "max_load": 5},
    {"id": "Agent_G2", "name": "Olivia Martinez", "role": "Junior Agent", "tier": "Junior", "load": 0, "max_load": 5},
]

# -------------------------------
# Lead Routing Quotas by Tier
# -------------------------------
SHARED_TIER_QUOTA = {
    "Top": 4,
    "Senior": 3,
    "Junior": 2
}

# -------------------------------
# Lead Assignment Functions
# -------------------------------
def assign_lead_by_score(score):
    if score >= 90:
        return assign_by_tier("Top")
    elif score >= 80:
        return assign_by_shared_tier(["Top", "Senior"])
    else:
        return assign_by_shared_tier(["Senior", "Junior"])


def assign_by_tier(tier):
    agents = [a for a in AGENT_POOL if a["tier"] == tier and a["load"] < a["max_load"]]
    if agents:
        selected = sorted(agents, key=lambda x: x["load"])[0]
        selected["load"] += 1
        update_agent_status(selected)
        return selected["name"]
    return None


def assign_by_shared_tier(tiers):
    eligible_agents = [
        a for a in AGENT_POOL
        if a["tier"] in tiers and a["load"] < a["max_load"]
    ]

    if not eligible_agents:
        return None

    # Group by tier
    grouped = {tier: [] for tier in tiers}
    for agent in eligible_agents:
        grouped[agent["tier"]].append(agent)

    # Select tier with available quota first
    for tier in tiers:
        if SHARED_TIER_QUOTA[tier] > 0 and grouped[tier]:
            agent = sorted(grouped[tier], key=lambda x: x["load"])[0]
            agent["load"] += 1
            update_agent_status(agent)
            SHARED_TIER_QUOTA[tier] -= 1
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


def reset_agent_load(agent_name):
    for agent in AGENT_POOL:
        if agent["name"] == agent_name:
            agent["load"] = 0
            update_agent_status(agent)
            break

# -------------------------------
# Property & Room Info
# -------------------------------
properties = [...]  # (Same as original: room availability listing)

# -------------------------------
# ALPS Scoring System
# -------------------------------
def urgency_score(move_in):
    days = (move_in - datetime.now().date()).days
    return 10 if days <= 4 else 8 if days <= 15 else 6 if days <= 30 else 3


def count_room_type(location, room_type):
    return sum(
        1 for p in properties if p['location'] == location
        for u in p['units']
        for r in u['rooms'] if not r['occupied'] and r['type'] == room_type
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
