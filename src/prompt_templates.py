from __future__ import annotations

from typing import Any, Dict


def destination_context(destination_id: str | None, knowledge_pack: Dict[str, Any]) -> Dict[str, Any] | None:
    if not destination_id:
        return None
    for d in knowledge_pack.get("destinations", []):
        if d.get("destination_id") == destination_id:
            return d
    return None


def compact_destination_list(knowledge_pack: Dict[str, Any]) -> str:
    rows = []
    for d in knowledge_pack.get("destinations", []):
        rows.append(
            f"- {d.get('destination')} ({d.get('country')}): "
            f"tags={', '.join(d.get('best_for_tags', []))}; "
            f"styles={', '.join(d.get('travel_styles', []))}"
        )
    return "\n".join(rows)


def build_profile_prompt(master_prompt: str, inspiration_text: str, uploaded_file_notes: str) -> str:
    return f"""
{master_prompt}

TASK:
Create a Travel Taste Profile from the user's inspiration.

USER INSPIRATION:
{inspiration_text}

UPLOADED FILE CONTEXT:
{uploaded_file_notes}

OUTPUT FORMAT:
Inferred from your content:
- Travel style:
- Interests:
- Pacing:
- Destination patterns:
- Aesthetic preferences:

Confidence:
- High / Medium / Low

Why:
- Briefly explain the user signals behind the profile.

What to verify:
- Note any dynamic or uncertain details that require live verification.

RULES:
- Do not infer sensitive attributes such as income, religion, politics, identity, or health.
- If input is sparse, say confidence is low and ask for minimal extra context.
- Keep it concise and friendly.
"""


def build_destination_prompt(
    master_prompt: str,
    profile: str,
    knowledge_pack: Dict[str, Any],
    constraints: Dict[str, Any],
) -> str:
    return f"""
{master_prompt}

TASK:
Recommend 3–5 destinations from the static knowledge pack based on the user's Travel Taste Profile and trip constraints.

TRAVEL TASTE PROFILE:
{profile}

TRIP CONSTRAINTS:
{constraints}

AVAILABLE DESTINATION KNOWLEDGE:
{compact_destination_list(knowledge_pack)}

OUTPUT FORMAT FOR EACH DESTINATION:
Destination:
Match Reason:
Best For:
Confidence:
What to verify:

RULES:
- Recommend 3–5 destinations maximum.
- Use only destinations from the available destination knowledge.
- Tie each recommendation to user preferences.
- Do not invent prices, availability, hours, live conditions, or hidden gems.
"""


def build_itinerary_prompt(
    master_prompt: str,
    profile: str,
    selected_destination: Dict[str, Any],
    constraints: Dict[str, Any],
) -> str:
    return f"""
{master_prompt}

TASK:
Generate a personalized itinerary for the selected destination.

TRAVEL TASTE PROFILE:
{profile}

SELECTED DESTINATION KNOWLEDGE:
{selected_destination}

TRIP CONSTRAINTS:
{constraints}

OUTPUT FORMAT:
Start with:
Inferred from your content:
- ...

General travel knowledge:
- ...

Needs verification:
- ...

Then provide itinerary:
Day [Day Number]:
Morning:
Afternoon:
Evening:
Why this fits:
What to verify:

RULES:
- Keep each day realistic and not overpacked.
- Group activities logically.
- Use broad categories/areas from the static knowledge pack.
- Include "What to verify" for hours, prices, reservations, availability, events, transit, weather, and booking details.
- Do not invent restaurant names, exact prices, hotel availability, live hours, or confirmed bookings.
"""


def build_refinement_prompt(
    master_prompt: str,
    current_itinerary: str,
    refinement_request: str,
    profile: str,
    constraints: Dict[str, Any],
) -> str:
    return f"""
{master_prompt}

TASK:
Refine the existing itinerary based on the user's request.

USER REQUEST:
{refinement_request}

CURRENT ITINERARY:
{current_itinerary}

TRAVEL TASTE PROFILE:
{profile}

TRIP CONSTRAINTS:
{constraints}

OUTPUT FORMAT:
Requested change:
What I changed:
Updated itinerary section:
What stayed the same:
What to verify:

RULES:
- Modify only what is necessary.
- Preserve previously learned preferences and constraints.
- Do not regenerate the full itinerary unless required.
- If the user asks for exact prices, live hours, booking status, or availability, use guardrail language and do not invent details.
"""
