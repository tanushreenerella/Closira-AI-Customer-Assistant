"""
Closira AI Customer Support Agent
Built with LangGraph + Groq (LLaMA 3.3 70B)
"""

import json
import os
import uuid
from datetime import datetime
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ── Load SOP ────────────────────────────────────────────────────────────────
with open("sop.json", "r") as f:
    SOP = json.load(f)

SOP_TEXT = json.dumps(SOP, indent=2)

# ── Groq client ──────────────────────────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# ── Escalation log ───────────────────────────────────────────────────────────
ESCALATION_LOG_FILE = "escalation_log.json"

def log_escalation(session_id: str, reason: str, conversation: list):
    entry = {
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "reason": reason,
        "conversation_snapshot": conversation[-6:]
    }
    existing = []
    if os.path.exists(ESCALATION_LOG_FILE):
        with open(ESCALATION_LOG_FILE, "r") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []
    existing.append(entry)
    with open(ESCALATION_LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)

# ── State ────────────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    messages: list
    session_id: str
    stage: Literal["faq", "qualify", "escalated", "summary"]
    unanswered_count: int
    qualification: dict
    escalation_reason: str
    sop_gaps: list
    conversation_ended: bool

# ── System prompts ────────────────────────────────────────────────────────────
SYSTEM_BASE = f"""You are Bloom, a friendly and professional AI assistant for Bloom Aesthetics Clinic — a premium aesthetics clinic offering Botox, dermal fillers, and free consultations.

YOUR STRICT RULES:
1. Answer ONLY from the SOP data below. Do NOT invent prices, services, policies, or any facts.
2. If a question is outside the SOP, say clearly: "I don't have that information right now" and offer to escalate.
3. Never give medical advice. Any medical/health question must be escalated immediately.
4. Be warm, concise, and professional — like a knowledgeable receptionist, not a robot.
5. Always respond in English.

SOP DATA:
{SOP_TEXT}

RESPONSE FORMAT (always return valid JSON, nothing else, no markdown fences):
{{
  "response": "<your reply to the customer>",
  "confidence": <0.0-1.0 float>,
  "escalate": <true/false>,
  "escalation_reason": "<reason if escalate=true, else null>",
  "stage_complete": <true/false>,
  "sop_gap": <true/false>
}}
"""

QUALIFY_QUESTIONS = [
    "What type of treatment are you most interested in: Botox, fillers, or a consultation?",
    "Have you had aesthetic treatments before, or would this be your first time?",
    "Are you looking to book an appointment soon, or are you still in the research phase?"
]

QUALIFY_PROMPT = """You are now in lead qualification mode. Your goal is to ask the customer 3 structured questions ONE AT A TIME to understand their needs. The 3 questions are:
1. What type of treatment are you most interested in? (Botox, Fillers, or Consultation)
2. Have you had aesthetic treatments before, or would this be your first time?
3. Are you looking to book an appointment soon, or still in the research phase?

Ask only one question at a time. Once you have collected all 3 answers, set stage_complete=true and summarise what was collected in your response.

Still follow the same JSON response format and escalation rules."""

# ── Helpers ───────────────────────────────────────────────────────────────────
def llm_call(system: str, messages: list) -> dict:
    """Call Groq and parse structured JSON response."""
    groq_messages = [{"role": "system", "content": system}] + messages
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=512,
        messages=groq_messages
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    try:
        parsed = json.loads(raw)
        # Clean up response field if Groq appended JSON blob inside it
        resp = str(parsed.get("response", ""))
        if "{" in resp:
            parsed["response"] = resp[:resp.index("{")].strip()
        return parsed
    except json.JSONDecodeError:
        return {
            "response": raw,
            "confidence": 0.5,
            "escalate": False,
            "escalation_reason": None,
            "stage_complete": False,
            "sop_gap": False
        }

def assistant_payload(result: dict) -> dict:
    """Keep assistant messages structured so the UI can read confidence/routing data."""
    return {
        "response": str(result.get("response", "")).strip(),
        "confidence": float(result.get("confidence", 0.7) or 0.7),
        "escalate": bool(result.get("escalate", False)),
        "escalation_reason": result.get("escalation_reason"),
        "stage_complete": bool(result.get("stage_complete", False)),
        "sop_gap": bool(result.get("sop_gap", False))
    }

def sentiment_check(text: str) -> tuple[bool, str]:
    """Quick sentiment guard — returns (is_negative, reason)."""
    anger_keywords = [
        "angry", "furious", "terrible", "horrible", "disgusting", "lawsuit",
        "unacceptable", "scam", "fraud", "worst", "never coming back",
        "this is ridiculous", "i demand", "incompetent", "hate"
    ]
    text_lower = text.lower()
    for kw in anger_keywords:
        if kw in text_lower:
            return True, f"Angry sentiment detected: '{kw}'"
    return False, ""

def explicit_escalation(text: str) -> tuple[bool, str]:
    """Check if user explicitly asks for a human."""
    phrases = ["speak to a human", "talk to someone", "real person",
               "human agent", "manager", "supervisor", "speak to staff"]
    text_lower = text.lower()
    for p in phrases:
        if p in text_lower:
            return True, "Customer requested human agent"
    return False, ""

def format_messages(state: AgentState) -> list:
    """Convert state messages to Groq format."""
    formatted = []
    for m in state["messages"]:
        role = m.type if hasattr(m, "type") else m.get("role", "user")
        content = m.content if hasattr(m, "content") else m.get("content", "")
        if role in ("ai", "assistant"):
            try:
                content = json.loads(content).get("response", content)
            except Exception:
                pass
        if role in ("human", "user"):
            formatted.append({"role": "user", "content": content})
        elif role in ("ai", "assistant"):
            formatted.append({"role": "assistant", "content": content})
    return formatted

# ── Nodes ─────────────────────────────────────────────────────────────────────
def faq_node(state: AgentState) -> AgentState:
    """Stage 1: Answer inbound questions from SOP only."""
    user_msg = state["messages"][-1].content if hasattr(state["messages"][-1], "content") else state["messages"][-1].get("content", "")

    is_negative, neg_reason = sentiment_check(user_msg)
    if is_negative:
        result = assistant_payload({
            "response": "I'm really sorry to hear you're feeling this way. I'm going to connect you with one of our team members right away so they can assist you properly.",
            "confidence": 1.0,
            "escalate": True,
            "escalation_reason": neg_reason
        })
        log_escalation(state["session_id"], neg_reason, format_messages(state))
        return {
            **state,
            "stage": "escalated",
            "escalation_reason": neg_reason,
            "messages": state["messages"] + [AIMessage(content=json.dumps(result))]
        }

    is_explicit, explicit_reason = explicit_escalation(user_msg)
    if is_explicit:
        result = assistant_payload({
            "response": "I'm flagging this conversation for our team right away. A Bloom Aesthetics specialist will be in touch with you shortly.",
            "confidence": 1.0,
            "escalate": True,
            "escalation_reason": explicit_reason
        })
        log_escalation(state["session_id"], explicit_reason, format_messages(state))
        return {
            **state,
            "stage": "escalated",
            "escalation_reason": explicit_reason,
            "messages": state["messages"] + [AIMessage(content=json.dumps(result))]
        }

    result = assistant_payload(llm_call(SYSTEM_BASE, format_messages(state)))

    new_unanswered = state["unanswered_count"]
    new_gaps = state["sop_gaps"].copy()

    if result.get("sop_gap"):
        new_unanswered += 1
        new_gaps.append(user_msg)
    else:
        new_unanswered = 0

    if result.get("escalate") or result.get("sop_gap") or new_unanswered >= 2:
        reason = result.get("escalation_reason") or "Question outside SOP data"
        result["escalate"] = True
        result["escalation_reason"] = reason
        log_escalation(state["session_id"], reason, format_messages(state))
        return {
            **state,
            "stage": "escalated",
            "escalation_reason": reason,
            "unanswered_count": new_unanswered,
            "sop_gaps": new_gaps,
            "messages": state["messages"] + [AIMessage(content=json.dumps(result))]
        }

    next_stage = "faq"
    if not result.get("sop_gap") and user_msg.lower().strip() not in {"hi", "hello", "hey", "hiya"}:
        next_stage = "qualify"
        result["response"] = f"{result['response']} {QUALIFY_QUESTIONS[0]}"

    return {
        **state,
        "stage": next_stage,
        "unanswered_count": new_unanswered,
        "sop_gaps": new_gaps,
        "messages": state["messages"] + [AIMessage(content=json.dumps(result))]
    }

def qualify_node(state: AgentState) -> AgentState:
    """Stage 2: Ask structured qualification questions."""
    user_msg = state["messages"][-1].content if hasattr(state["messages"][-1], "content") else state["messages"][-1].get("content", "")

    is_negative, neg_reason = sentiment_check(user_msg)
    if is_negative:
        result = assistant_payload({
            "response": "I'm really sorry to hear you're feeling this way. I'm going to connect you with one of our team members right away so they can assist you properly.",
            "confidence": 1.0,
            "escalate": True,
            "escalation_reason": neg_reason
        })
        log_escalation(state["session_id"], neg_reason, format_messages(state))
        return {
            **state,
            "stage": "escalated",
            "escalation_reason": neg_reason,
            "messages": state["messages"] + [AIMessage(content=json.dumps(result))]
        }

    new_qual = state["qualification"].copy()
    q_count = len(new_qual)
    if q_count < len(QUALIFY_QUESTIONS):
        new_qual[f"answer_{q_count + 1}"] = user_msg

    if len(new_qual) >= len(QUALIFY_QUESTIONS):
        result = assistant_payload({
            "response": "Thank you, that helps. I have your treatment interest, prior experience, and booking readiness. I'll prepare a short session summary for our team.",
            "confidence": 1.0,
            "stage_complete": True
        })
        next_stage = "summary"
    else:
        result = assistant_payload({
            "response": QUALIFY_QUESTIONS[len(new_qual)],
            "confidence": 1.0,
            "stage_complete": False
        })
        next_stage = "qualify"

    return {
        **state,
        "stage": next_stage,
        "qualification": new_qual,
        "messages": state["messages"] + [AIMessage(content=json.dumps(result))]
    }

def escalation_node(state: AgentState) -> AgentState:
    """Stage 3: Handle escalation gracefully."""
    return {**state, "conversation_ended": True}

def summary_node(state: AgentState) -> AgentState:
    """Stage 4: Generate structured session summary."""
    history = format_messages(state)
    qual = state.get("qualification", {})
    gaps = state.get("sop_gaps", [])

    summary_prompt = f"""Based on this full conversation, generate a structured customer session summary.

Qualification data collected: {json.dumps(qual)}
SOP gaps identified: {json.dumps(gaps)}

Return ONLY valid JSON, no markdown fences:
{{
  "customer_intent": "<one sentence describing what the customer wants>",
  "key_details_collected": {{
    "treatment_interest": "<treatment or null>",
    "experience_level": "<first-time or experienced or null>",
    "booking_readiness": "<ready to book / researching / null>"
  }},
  "sop_gaps": ["<question 1>", "<question 2>"],
  "recommended_next_action": "<what the team should do next>",
  "escalated": false,
  "escalation_reason": null
}}"""

    groq_messages = [{"role": "system", "content": summary_prompt}] + history
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=512,
        messages=groq_messages
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    try:
        summary = json.loads(raw)
    except Exception:
        summary = {"raw_summary": raw}

    summary_file = f"summary_{state['session_id'][:8]}.json"
    with open(summary_file, "w") as f:
        json.dump({"session_id": state["session_id"], "timestamp": datetime.utcnow().isoformat() + "Z", **summary}, f, indent=2)

    result = assistant_payload({
        "response": "Session summary saved for the Bloom Aesthetics team. Thank you for chatting with Bloom.",
        "confidence": 1.0,
        "stage_complete": True
    })

    return {
        **state,
        "conversation_ended": True,
        "messages": state["messages"] + [AIMessage(content=json.dumps(result))]
    }

# ── Router ────────────────────────────────────────────────────────────────────
def router(state: AgentState) -> str:
    stage = state["stage"]
    if state.get("conversation_ended"):
        return END
    if stage == "faq":       return "faq"
    if stage == "qualify":   return "qualify"
    if stage == "escalated": return "escalation"
    if stage == "summary":   return "summary"
    return END

def after_qualify_router(state: AgentState) -> str:
    if state["stage"] == "summary":
        return "summary"
    if state["stage"] == "escalated":
        return "escalation"
    return END

# ── Build Graph ───────────────────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("faq", faq_node)
    graph.add_node("qualify", qualify_node)
    graph.add_node("escalation", escalation_node)
    graph.add_node("summary", summary_node)

    graph.set_conditional_entry_point(router, {
        "faq": "faq",
        "qualify": "qualify",
        "escalation": "escalation",
        "summary": "summary",
        END: END
    })
    graph.add_edge("faq", END)
    graph.add_conditional_edges("qualify", after_qualify_router, {
        "summary": "summary",
        "escalation": "escalation",
        END: END
    })
    graph.add_edge("escalation", END)
    graph.add_edge("summary", END)

    return graph.compile()

APP = build_graph()

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_initial_state(session_id: str = None) -> AgentState:
    if not session_id:
        session_id = str(uuid.uuid4())
    return {
        "messages": [],
        "session_id": session_id,
        "stage": "faq",
        "unanswered_count": 0,
        "qualification": {},
        "escalation_reason": "",
        "sop_gaps": [],
        "conversation_ended": False
    }
