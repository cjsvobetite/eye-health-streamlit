import os
import random
import uuid
from typing import Any

import streamlit as st
from openai import OpenAI
from supabase import Client, create_client

st.set_page_config(
    page_title="Eye Health Guide",
    page_icon="👁️",
    layout="centered",
)

SURVEY_QUESTIONS = [
    {
        "key": "age_group",
        "section": "Basic Information",
        "question": "Age group",
        "type": "radio",
        "options": ["Under 18", "18-39", "40-59", "60 and above"],
        "weights": {"Under 18": 0, "18-39": 0, "40-59": 2, "60 and above": 4},
        "category": "demographic",
    },
    {
        "key": "sex",
        "section": "Basic Information",
        "question": "Biological sex",
        "type": "radio",
        "options": ["Male", "Female", "Prefer not to say"],
        "weights": {},
        "category": "demographic",
    },
    {
        "key": "ethnicity",
        "section": "Basic Information",
        "question": "Ethnicity (optional)",
        "type": "radio",
        "options": [
            "East Asian",
            "African / African American",
            "Hispanic / Latino",
            "White / Caucasian",
            "Other / Prefer not to say",
        ],
        "weights": {
            "African / African American": 2,
            "Hispanic / Latino": 1,
        },
        "category": "demographic",
    },
    {
        "key": "family_history",
        "section": "Family & Medical History",
        "question": "Family history of glaucoma?",
        "type": "radio",
        "options": ["Yes", "No", "I don't know"],
        "weights": {"Yes": 4, "I don't know": 1},
        "category": "genetic",
    },
    {
        "key": "conditions",
        "section": "Family & Medical History",
        "question": "Diagnosed conditions (check all that apply)",
        "type": "multiselect",
        "options": [
            "Type 2 diabetes",
            "High blood pressure (hypertension)",
            "High myopia (-6.00 D or more)",
            "Sleep apnea",
        ],
        "weights": {
            "Type 2 diabetes": 2,
            "High blood pressure (hypertension)": 1,
            "High myopia (-6.00 D or more)": 2,
            "Sleep apnea": 1,
        },
        "category": "systemic",
    },
    {
        "key": "medications",
        "section": "Family & Medical History",
        "question": "Regular medications?",
        "type": "radio",
        "options": [
            "Yes - corticosteroids",
            "Yes - other medications",
            "No",
        ],
        "weights": {"Yes - corticosteroids": 3},
        "category": "systemic",
    },
    {
        "key": "screen_time",
        "section": "Lifestyle",
        "question": "Daily screen time",
        "type": "radio",
        "options": ["< 2 hours", "2-4 hours", "5-7 hours", ">= 8 hours"],
        "weights": {"5-7 hours": 1, ">= 8 hours": 2},
        "category": "lifestyle",
    },
    {
        "key": "breaks",
        "section": "Lifestyle",
        "question": "Take 20-20-20 breaks?",
        "type": "radio",
        "options": ["Consistently", "Sometimes", "Rarely or never"],
        "weights": {"Rarely or never": 1},
        "category": "lifestyle",
    },
    {
        "key": "exercise",
        "section": "Lifestyle",
        "question": "Weekly moderate-vigorous exercise",
        "type": "radio",
        "options": ["< 1 hour", "1-3 hours", "4-6 hours", "> 6 hours"],
        "weights": {"< 1 hour": 2, "1-3 hours": 1},
        "category": "lifestyle",
    },
    {
        "key": "smoking",
        "section": "Smoking",
        "question": "Current smoking / vaping?",
        "type": "radio",
        "options": ["Currently", "Past only", "Never"],
        "weights": {"Currently": 3, "Past only": 1},
        "category": "lifestyle",
    },
    {
        "key": "secondhand",
        "section": "Smoking",
        "question": "Secondhand smoke exposure",
        "type": "radio",
        "options": ["Frequently", "Sometimes", "Rarely or never"],
        "weights": {"Frequently": 1},
        "category": "lifestyle",
    },
    {
        "key": "last_exam",
        "section": "Eye Exam History",
        "question": "Last comprehensive eye exam",
        "type": "radio",
        "options": ["Within 1 year", "1-2 years ago", "> 2 years ago", "Never"],
        "weights": {"> 2 years ago": 2, "Never": 3},
        "category": "screening",
    },
    {
        "key": "high_iop",
        "section": "Eye Exam History",
        "question": "Ever told IOP was elevated?",
        "type": "radio",
        "options": ["Yes", "No", "Never tested"],
        "weights": {"Yes": 4, "Never tested": 1},
        "category": "screening",
    },
    {
        "key": "symptoms",
        "section": "Eye Exam History",
        "question": "Recent symptoms (check all that apply)",
        "type": "multiselect",
        "options": [
            "Blurry / hazy vision",
            "Halos around lights",
            "Loss of peripheral vision",
            "Eye pain or headaches",
            "Frequent eye fatigue / dryness",
        ],
        "weights": {
            "Blurry / hazy vision": 1,
            "Halos around lights": 3,
            "Loss of peripheral vision": 4,
            "Eye pain or headaches": 2,
            "Frequent eye fatigue / dryness": 1,
        },
        "category": "symptoms",
    },
    {
        "key": "leafy_greens",
        "section": "Diet",
        "question": "Leafy green consumption",
        "type": "radio",
        "options": ["Daily", "3-5x/week", "1-2x/week", "Rarely or never"],
        "weights": {"1-2x/week": 1, "Rarely or never": 2},
        "category": "lifestyle",
    },
    {
        "key": "water",
        "section": "Diet",
        "question": "Daily water intake",
        "type": "radio",
        "options": ["< 4 cups", "4-6 cups", "7-8 cups", "> 8 cups"],
        "weights": {"< 4 cups": 1},
        "category": "lifestyle",
    },
]

QUOTES = [
    {
        "theme": "screen_breaks",
        "text": "Your eyes work hard all day. Give them 20 seconds of distance.",
    },
    {
        "theme": "screen_breaks",
        "text": "Small breaks protect big focus. Try the 20-20-20 rule today.",
    },
    {
        "theme": "screening",
        "text": "Glaucoma often whispers, not shouts. Regular eye exams help you hear it early.",
    },
    {
        "theme": "screening",
        "text": "A single eye pressure number is a snapshot. A full eye exam tells the story.",
    },
    {
        "theme": "daily_habits",
        "text": "Clear vision tomorrow starts with small habits today.",
    },
    {
        "theme": "daily_habits",
        "text": "Your eyes are part of your whole body. Sleep, movement, and hydration matter.",
    },
    {
        "theme": "general",
        "text": "Eye care is not one big action. It is a quiet routine repeated daily.",
    },
]

SYSTEM_PROMPT = """You are an eye health educator.
You are NOT a doctor.

Rules:
1. Do not diagnose.
2. Do not say the user has or does not have glaucoma.
3. Give 4-6 practical lifestyle suggestions.
4. Mention regular comprehensive eye exams.
5. Explain that glaucoma can be silent.
6. Explain that a single IOP reading can vary, so full eye exams matter.
7. Use friendly plain English.
8. Keep it concise.

Return Markdown with:
## Your Personalized Eye Health Sheet
### Top Priority
### Daily Habits to Try
### When to See an Eye Doctor
### Quick Facts
"""


def get_setting(name: str) -> str | None:
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name)
    except Exception:
        return None


@st.cache_resource
def get_supabase_client() -> Client | None:
    url = get_setting("SUPABASE_URL")
    key = get_setting("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def calculate_risk(responses: dict[str, Any]) -> dict[str, Any]:
    total = 0
    by_category: dict[str, int] = {}
    triggered: list[str] = []

    for question in SURVEY_QUESTIONS:
        answer = responses.get(question["key"])
        if answer is None:
            continue

        if question["type"] == "radio":
            weight = question["weights"].get(answer, 0)
            total += weight
            category = question["category"]
            by_category[category] = by_category.get(category, 0) + weight
            if weight >= 2:
                triggered.append(f'{question["question"]}: {answer}')

        elif question["type"] == "multiselect":
            for choice in answer:
                weight = question["weights"].get(choice, 0)
                total += weight
                category = question["category"]
                by_category[category] = by_category.get(category, 0) + weight
                if weight >= 2:
                    triggered.append(f'{question["question"]}: {choice}')

    if total <= 3:
        level = "Low"
        emoji = "🟢"
    elif total <= 8:
        level = "Moderate"
        emoji = "🟡"
    else:
        level = "High"
        emoji = "🔴"

    return {
        "score": total,
        "level": level,
        "emoji": emoji,
        "by_category": by_category,
        "triggered": triggered,
    }


def choose_quote(theme: str = "general") -> dict[str, str]:
    candidates = [quote for quote in QUOTES if quote["theme"] == theme]
    if not candidates:
        candidates = QUOTES
    return random.choice(candidates)


def theme_from_risk(risk: dict[str, Any]) -> str:
    by_category = risk.get("by_category", {})
    if by_category.get("screening", 0) >= 2:
        return "screening"
    if by_category.get("lifestyle", 0) >= 2:
        return "screen_breaks"
    return "daily_habits"


def format_responses(responses: dict[str, Any]) -> str:
    lines = []
    for key, value in responses.items():
        if isinstance(value, list):
            value = ", ".join(value) if value else "None"
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def generate_advice(responses: dict[str, Any], risk: dict[str, Any]) -> str:
    api_key = get_setting("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    client = OpenAI(api_key=api_key)
    user_message = f"""Participant survey responses:
{format_responses(responses)}

Calculated risk:
- Score: {risk['score']}
- Level: {risk['level']}
- Triggered concerns: {', '.join(risk['triggered']) if risk['triggered'] else 'None'}
- Category breakdown: {risk['by_category']}

Generate a personalized educational eye health sheet."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.4,
        max_tokens=800,
    )
    return response.choices[0].message.content or ""


def generate_result(responses: dict[str, Any], device_id: str) -> dict[str, Any]:
    risk = calculate_risk(responses)

    try:
        advice = generate_advice(responses, risk)
    except Exception as error:
        advice = (
            "## Your Personalized Eye Health Sheet\n\n"
            "AI advice is temporarily unavailable.\n\n"
            "Please consider regular comprehensive eye exams, especially if you have symptoms "
            "or risk factors. This app is educational and does not diagnose medical conditions.\n\n"
            f"Error: {error}"
        )

    quote_theme = theme_from_risk(risk)
    quote = choose_quote(quote_theme)

    supabase = get_supabase_client()
    if supabase:
        try:
            supabase.table("survey_responses").insert(
                {
                    "responses": responses,
                    "risk": risk,
                    "advice": advice,
                    "device_id": device_id,
                }
            ).execute()
        except Exception as error:
            st.warning(f"The result was generated, but it could not be saved: {error}")

    return {
        "risk": risk,
        "advice": advice,
        "daily_quote": quote,
        "recommended_quote_theme": quote_theme,
    }


def initialize_state() -> None:
    defaults = {
        "step": "intro",
        "responses": {},
        "result": None,
        "device_id": str(uuid.uuid4()),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_over() -> None:
    st.session_state.step = "intro"
    st.session_state.responses = {}
    st.session_state.result = None
    for question in SURVEY_QUESTIONS:
        st.session_state.pop(f'question_{question["key"]}', None)


def render_intro() -> None:
    st.title("👁️ Eye Health Guide")
    st.write("A short educational survey for eye health awareness.")

    with st.container(border=True):
        st.subheader("What this app does")
        st.markdown(
            "- Asks quick questions about lifestyle and eye health\n"
            "- Estimates an educational risk level\n"
            "- Generates a personalized guidance sheet\n"
            "- Shows an eye health quote"
        )

    st.warning(
        "Educational use only. This app does not diagnose, treat, or replace "
        "medical advice. If you have eye symptoms or concerns, see an eye doctor."
    )

    if st.button("Start Survey", type="primary", use_container_width=True):
        st.session_state.step = "survey"
        st.rerun()


def render_survey() -> None:
    st.title("Survey")
    st.caption("Please answer each single-choice question. Multi-select questions may be left empty.")

    responses: dict[str, Any] = {}
    current_section = None

    with st.form("eye_health_survey"):
        for question in SURVEY_QUESTIONS:
            if question["section"] != current_section:
                current_section = question["section"]
                st.subheader(current_section)

            widget_key = f'question_{question["key"]}'
            if question["type"] == "radio":
                responses[question["key"]] = st.radio(
                    question["question"],
                    options=question["options"],
                    index=None,
                    key=widget_key,
                )
            else:
                responses[question["key"]] = st.multiselect(
                    question["question"],
                    options=question["options"],
                    key=widget_key,
                )

        submitted = st.form_submit_button(
            "Submit & Get My Sheet",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        missing = [
            question["question"]
            for question in SURVEY_QUESTIONS
            if question["type"] == "radio" and responses.get(question["key"]) is None
        ]
        if missing:
            st.error(f"Please answer: {missing[0]}")
            return

        st.session_state.responses = responses
        with st.spinner("Generating your result..."):
            st.session_state.result = generate_result(
                responses,
                st.session_state.device_id,
            )
        st.session_state.step = "result"
        st.rerun()


def render_result() -> None:
    result = st.session_state.result
    if not result:
        st.session_state.step = "intro"
        st.rerun()

    risk = result["risk"]
    st.title("Your Result")

    with st.container(border=True):
        st.metric(
            label="Educational risk level",
            value=f'{risk["emoji"]} {risk["level"]}',
            delta=f'Score: {risk["score"]}',
            delta_color="off",
        )

    if risk["triggered"]:
        with st.container(border=True):
            st.subheader("What contributed to your score")
            for item in risk["triggered"]:
                st.markdown(f"- {item}")

    with st.container(border=True):
        st.subheader("Today’s Eye Health Quote")
        st.markdown(f'> “{result["daily_quote"]["text"]}”')

    with st.container(border=True):
        st.subheader("Personalized Sheet")
        st.markdown(result["advice"])

    st.warning(
        "This result is for education and awareness only. It is not a diagnosis "
        "and does not replace a comprehensive eye examination."
    )

    if st.button("Start Over", use_container_width=True):
        start_over()
        st.rerun()


initialize_state()

if st.session_state.step == "intro":
    render_intro()
elif st.session_state.step == "survey":
    render_survey()
else:
    render_result()
