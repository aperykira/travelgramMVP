from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

KEYWORDS = {
    "food": ["food", "street food", "market", "seafood", "restaurant", "dining", "izakaya", "tasting"],
    "cafes": ["cafe", "cafés", "coffee", "matcha", "bakery"],
    "culture": ["temple", "museum", "culture", "historic", "traditional", "architecture", "bookstore"],
    "nature": ["hike", "hiking", "mountain", "lake", "nature", "trail", "garden", "outdoor"],
    "nightlife": ["nightlife", "bar", "club", "evening"],
    "shopping": ["shopping", "boutique", "shops", "market"],
    "views": ["view", "viewpoint", "scenic", "sunset", "riverfront", "coastal"],
    "relaxed": ["quiet", "slow", "relaxed", "calm", "peaceful", "downtime"],
    "aesthetic": ["aesthetic", "cinematic", "tiles", "boutique", "pretty", "beautiful", "minimalist"],
}

DESTINATION_ALIASES = {
    "kyoto": "kyoto_japan",
    "japan": "kyoto_japan",
    "lisbon": "lisbon_portugal",
    "portugal": "lisbon_portugal",
    "banff": "banff_canada",
    "canada": "banff_canada",
    "porto": "porto_portugal",
    "paris": "paris_france",
    "france": "paris_france",
}


def _contains_any(text: str, words: List[str]) -> bool:
    text_l = text.lower()
    return any(w.lower() in text_l for w in words)


def extract_profile_demo(inspiration_text: str, uploaded_file_notes: str = "") -> str:
    text = f"{inspiration_text}\n{uploaded_file_notes}".lower()
    interests = [k for k, words in KEYWORDS.items() if _contains_any(text, words)]

    dests = []
    for alias, dest_id in DESTINATION_ALIASES.items():
        if alias in text and dest_id not in dests:
            dests.append(dest_id)

    pace = "Relaxed / slow-paced" if "relaxed" in interests else "Moderate"
    style = []
    if "aesthetic" in interests:
        style.append("Aesthetic traveler")
    if "nature" in interests:
        style.append("Outdoor / nature-focused")
    if "food" in interests or "cafes" in interests:
        style.append("Food explorer")
    if "culture" in interests:
        style.append("Cultural explorer")
    if not style:
        style.append("Open-ended traveler")

    confidence = "Medium"
    if len(interests) >= 4 or dests:
        confidence = "High"
    elif len(interests) <= 1:
        confidence = "Low"

    interests_display = ", ".join(interests) if interests else "Not enough signal yet"
    dest_display = ", ".join(dests) if dests else "No clear destination signal yet"
    style_display = ", ".join(style)

    return f"""Inferred from your content:
- Travel style: {style_display}
- Interests: {interests_display}
- Pacing: {pace}
- Destination patterns: {dest_display}
- Aesthetic preferences: {"visual/aesthetic travel signals detected" if "aesthetic" in interests else "not enough signal yet"}

Confidence:
- {confidence}

Why:
- I detected signals from the inspiration text and uploaded file context, such as: {interests_display}.

What to verify:
- Any current hours, prices, availability, reservations, event schedules, transit changes, or booking details should be verified through live sources.
"""


def _profile_tokens(profile: str) -> set:
    return set(re.findall(r"[a-zA-Z]+", profile.lower()))


def recommend_destinations_demo(profile: str, knowledge_pack: Dict[str, Any], constraints: Dict[str, Any]) -> str:
    tokens = _profile_tokens(profile)
    scored: List[Tuple[int, Dict[str, Any]]] = []
    for d in knowledge_pack.get("destinations", []):
        tags = " ".join(d.get("best_for_tags", []) + d.get("travel_styles", []) + d.get("known_for_stable", []))
        tag_tokens = _profile_tokens(tags)
        score = len(tokens.intersection(tag_tokens))
        scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)

    output = []
    for score, d in scored[:5]:
        confidence = "High" if score >= 4 else "Medium" if score >= 2 else "Low"
        best_for = ", ".join(d.get("best_for_tags", [])[:5])
        output.append(
            f"""Destination:
{d.get('destination')}, {d.get('country')}

Match Reason:
Based on your profile, this appears to match interests like {best_for}.

Best For:
{best_for}

Confidence:
{confidence}

What to verify:
Current prices, availability, opening hours, events, transit details, and booking requirements.
"""
        )
    return "\n---\n".join(output)


def generate_itinerary_demo(profile: str, destination: Dict[str, Any], constraints: Dict[str, Any]) -> str:
    days = int(constraints.get("days", 3) or 3)
    days = max(1, min(days, 10))
    modules = destination.get("sample_day_modules", [])
    areas = destination.get("areas_or_neighborhoods", [])
    experiences = destination.get("experience_categories", [])

    inferred = "This itinerary uses the Travel Taste Profile and the selected destination knowledge pack."
    general = destination.get("summary", "")
    verify = "Specific hours, current prices, reservations, availability, events, weather, and transit details."

    lines = [
        "Inferred from your content:",
        f"- {inferred}",
        "",
        "General travel knowledge:",
        f"- {general}",
        "",
        "Needs verification:",
        f"- {verify}",
        ""
    ]

    for i in range(1, days + 1):
        module = modules[(i - 1) % len(modules)] if modules else {}
        area = areas[(i - 1) % len(areas)] if areas else {"name": "a relevant neighborhood", "best_for": []}
        exp = experiences[(i - 1) % len(experiences)] if experiences else "local exploration"
        lines.extend([
            f"Day {i}:",
            f"Morning: {module.get('morning', 'Explore ' + area.get('name', 'a relevant area') + ' with a focus on ' + exp + '.')}",
            f"Afternoon: {module.get('afternoon', 'Add a nearby experience related to ' + exp + ', keeping travel time manageable.')}",
            f"Evening: {module.get('evening', 'Keep the evening flexible for dinner, rest, or a relaxed walk.')}",
            f"Why this fits: {module.get('why_this_fits', 'This aligns with your inferred travel interests while keeping the day realistic.')}",
            f"What to verify: {', '.join(module.get('what_to_verify', destination.get('verification_required', [])))}",
            ""
        ])
    return "\n".join(lines)


def refine_itinerary_demo(current_itinerary: str, request: str, profile: str, constraints: Dict[str, Any]) -> str:
    req = request.lower()
    if "cheap" in req or "budget" in req or "cheaper" in req:
        change = "I’ll swap premium-style options for more budget-conscious alternatives, but I won’t estimate exact prices without live data."
        updated = "- Replace premium-style activities with free/low-cost walking routes, markets, public viewpoints, and self-guided exploration.\n- Compare budget-friendly accommodation areas rather than assuming exact hotel prices."
    elif "relaxed" in req or "slower" in req or "downtime" in req:
        change = "I’ll reduce the number of activities per day, add more open time, and keep the experiences most aligned with your travel style."
        updated = "- Remove one activity block from each day.\n- Add flexible café/rest time between major activities.\n- Keep only the highest-fit experiences."
    elif "food" in req or "cafe" in req or "market" in req:
        change = "I’ll add more food-focused experiences while avoiding claims about exact menus, hours, or current availability."
        updated = "- Add food market, café, or dining-area exploration blocks.\n- Keep restaurant-specific details as items to verify live."
    elif "nature" in req or "hike" in req:
        change = "I’ll add more nature-focused experiences while keeping pacing realistic."
        updated = "- Add scenic walks, gardens, parks, viewpoints, or hiking modules depending on the destination.\n- Flag weather/trail conditions for verification."
    else:
        change = "I’ll update the itinerary based on your request while preserving the original constraints."
        updated = "- Adjust the relevant itinerary sections only.\n- Keep the trip length, destination, and known preferences consistent."

    return f"""Requested change:
{request}

What I changed:
{change}

Updated itinerary section:
{updated}

What stayed the same:
- Destination, trip length, and core inferred preferences remain unchanged unless you asked to change them.

What to verify:
- Exact prices, current hours, availability, reservations, weather, transit changes, and booking details should be verified through live sources.
"""
