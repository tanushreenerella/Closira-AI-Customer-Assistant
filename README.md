# Closira — AI Customer Support Agent
### Bloom Aesthetics Clinic · Built for AI Engineering Internship Assignment

A stateful AI customer support workflow built using **LangGraph + Groq (Llama 3.3 70B)**. The system handles customer conversations across four stages:

- FAQ answering from business SOP data
- Lead qualification
- Escalation detection
- Structured conversation summaries

The workflow is designed to prioritise **SOP grounding, safe escalation behaviour, and traceable state transitions**.

---

# Architecture Overview

```text
Customer Message
        │
        ▼
Pre-flight Checks
• Angry sentiment detection
• Explicit human escalation request
        │
        ▼
Router (checks current state["stage"])
        │
        ├── faq_node
        │       │
        │       ├── SOP-grounded answer
        │       ├── Detect SOP gaps
        │       └── Update stage
        │
        ├── qualify_node
        │       │
        │       └── Collect structured lead info
        │
        ├── escalation_node
        │       │
        │       └── End conversation + log escalation
        │
        └── summary_node
                │
                └── Generate structured JSON summary

Updated state
        │
        ▼
Router decides next node
```

The workflow is **state-driven**. Each node updates `AgentState`, and routing decisions determine which node executes next.

---

# Workflow Stages

### 1. FAQ Answering
Respond to customer questions using only `sop.json`.

Goals:

- Prevent hallucinations
- Restrict answers to business SOP
- Escalate unsupported queries

---

### 2. Lead Qualification

Collect:

- Treatment interest
- Prior experience
- Booking readiness

Questions are asked one at a time and stored in shared state.

---

### 3. Escalation Detection

Escalation may occur due to:

- Angry/frustrated sentiment
- Explicit request for a human
- Consecutive SOP gaps
- Model self-flagging uncertainty
- Prompt-level medical safety instructions

All escalation reasons are logged.

---

### 4. Conversation Summary

Generate structured output:

- Customer intent
- Qualification answers
- SOP gaps
- Recommended next action

Saved automatically as JSON.

---

# Features

| Feature | Description |
|---------|-------------|
| SOP grounded responses | AI answers only from `sop.json` |
| Hallucination prevention | Prompt constraints prevent unsupported claims |
| Typed state | Shared `AgentState` stores stage, qualification, gaps, escalation |
| LangGraph workflow | Router-driven node execution |
| Escalation logging | Timestamped logs with conversation snapshot |
| Lead qualification | Structured multi-step qualification flow |
| Session summary | Auto-generated JSON summaries |
| Confidence score | Every response returns confidence metadata |
| Web UI | FastAPI + WebSocket interface |
| CLI mode | Terminal-based testing |

---

# Why LangGraph?

LangGraph was chosen because the workflow requires **explicit state transitions** between FAQ answering, qualification, escalation, and summarisation.

Compared to a single prompt chain, graph-based execution provides:

- Deterministic routing
- Shared memory via state
- Easier debugging
- Clear workflow separation

---

# Project Structure

```text
closira/
│
├── agent.py
│      LangGraph nodes, prompts, routing, workflow
│
├── server.py
│      FastAPI backend + WebSocket integration + UI
│
├── cli.py
│      Command line testing interface
│
├── sop.json
│      Business knowledge source
│
├── prompt_design.md
│      Prompt reasoning, hallucination prevention,
│      escalation logic, persona design
│
├── escalation_log.json
│      Generated escalation records
│
├── summary_<id>.json
│      Generated session summaries
│
├── requirements.txt
│
└── test_transcripts/
       ├── in_sop.md
       ├── escalation.md
       ├── qualification.md
       └── summary.md
```

---

# Setup

## Prerequisites

- Python 3.10+
- Groq API key

---

Install dependencies:

```bash
pip install groq langgraph langchain-core fastapi uvicorn websockets python-dotenv
```

Set API key:

Linux/Mac:

```bash
export GROQ_API_KEY=gsk_xxx
```

Windows:

```cmd
set GROQ_API_KEY=gsk_xxx
```

---

# Running

## Option 1 — Web Interface (Recommended)

Run:

```bash
uvicorn server:app --reload --port 8000
```

Open:

```txt
http://localhost:8000
```

Features:

- Live conversation UI
- Current stage indicator
- Confidence score display
- SOP gaps panel
- Qualification data panel
- New session support

---

## Option 2 — CLI Mode

Run:

```bash
python cli.py
```

Type:

```txt
quit
```

to end session and generate summary.

---

# Model Used

Model:

```txt
llama-3.3-70b-versatile
```

via Groq API.

Chosen because:

- Fast inference
- Good structured JSON generation
- Suitable latency for conversational workflows
- Cost effective for prototypes

---

# Escalation Logic

Escalation checks happen in this approximate priority:

1. Angry sentiment keywords

Example:

```txt
I am furious
This is unacceptable
```

↓

Escalate

---

2. Explicit human request

Example:

```txt
I want to speak to a manager
```

↓

Escalate

---

3. SOP gaps

Repeated unsupported questions trigger escalation.

---

4. Model self-flagging

LLM returns:

```json
{
 "escalate": true
}
```

↓

Escalate

---

Escalations are stored in:

```txt
escalation_log.json
```

---

# Trade-offs / Limitations

Current limitations:

### Sentiment detection

Keyword-based detection is simple but lacks nuance.

Production systems may use:

- Dedicated sentiment models
- Tool calling
- LLM classification

---

### Session persistence

Sessions exist in memory.

Production systems would use:

- Redis
- PostgreSQL
- Vector databases

---

### Static SOP

Only one SOP source exists.

Production systems require:

- Multi-business support
- Dynamic SOP updates

---

### Authentication

No auth layer implemented.

Out of scope for assignment.

---

### Streaming responses

Responses are returned fully.

Streaming tokens would improve UX.

---

# Demo Scenarios Included

Test transcripts demonstrate:

✅ In-SOP question

✅ Out-of-scope question

✅ Angry customer escalation

✅ Lead qualification

✅ Conversation summary generation

---

# Author

**Tanushree Venkata Nerella**  
B.Tech Computer Science  
Manipal University Jaipur (2027)

GitHub: <your-link>

LinkedIn: <your-link>

Email:
tanushreenerella697@gmail.com
https://www.loom.com/share/96ff1173196f4353a0d8c2759993dcb0