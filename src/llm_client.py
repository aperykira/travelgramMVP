from __future__ import annotations

import base64
import os
from typing import List, Optional

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def call_openai_text(prompt: str, model: str | None = None, api_key: str | None = None) -> str:
    if OpenAI is None:
        raise RuntimeError("OpenAI package is not installed. Run: pip install -r requirements.txt")

    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("No OpenAI API key found. Use Demo Mode or set OPENAI_API_KEY.")

    client = OpenAI(api_key=key)
    chosen_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=chosen_model,
        messages=[
            {"role": "system", "content": "You are a factual, concise AI travel planning assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content or ""


def call_openai_with_images(
    prompt: str,
    image_files: Optional[List] = None,
    model: str | None = None,
    api_key: str | None = None,
) -> str:
    if OpenAI is None:
        raise RuntimeError("OpenAI package is not installed. Run: pip install -r requirements.txt")

    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("No OpenAI API key found. Use Demo Mode or set OPENAI_API_KEY.")

    client = OpenAI(api_key=key)
    chosen_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    content = [{"type": "text", "text": prompt}]

    for file in image_files or []:
        raw = file.getvalue()
        encoded = base64.b64encode(raw).decode("utf-8")
        mime = file.type or "image/png"
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{encoded}"}
        })

    response = client.chat.completions.create(
        model=chosen_model,
        messages=[
            {"role": "system", "content": "You are a factual, concise AI travel planning assistant."},
            {"role": "user", "content": content},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content or ""
