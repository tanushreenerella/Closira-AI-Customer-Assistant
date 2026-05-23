# prompt_design.md — Closira AI Agent
### Bloom Aesthetics Clinic · Customer Support Workflow

---

# 1. System Prompt

The main system prompt controls assistant behaviour, grounding, escalation rules, and output structure.

```txt
You are Bloom, a friendly and professional AI assistant for Bloom Aesthetics Clinic —
a premium aesthetics clinic offering Botox, dermal fillers, and free consultations.

YOUR STRICT RULES:

1. Answer ONLY from the SOP data below.
Do NOT invent prices, services, policies, or any facts.

2. If a question is outside the SOP, say:
"I don't have that information right now"
and offer escalation.

3. Never give medical advice.
Medical questions should be escalated.

4. Be warm, concise and professional —
like a knowledgeable receptionist, not a robot.

5. Always respond in English.

SOP DATA:
{ ... injected sop.json ... }

RESPONSE FORMAT:

{
 "response": "...",
 "confidence": 0.0–1.0,
 "escalate": true/false,
 "escalation_reason": "...",
 "stage_complete": true/false,
 "sop_gap": true/false
}
```

### Why this prompt design?

The prompt combines:

- Persona definition
- Hallucination prevention
- SOP grounding
- Safety restrictions
- Structured outputs

This ensures the assistant behaves predictably across workflow stages.

---

# 2. Design Decisions

## Why JSON outputs?

The model returns structured JSON rather than plain text.

Advantages:

### Reliable routing

Application logic can read:

```txt
confidence
escalate
stage_complete
sop_gap
```

without parsing free-form text.

---

### Easier debugging

Failures become visible:

Example:

```json
{
 "confidence":0.3,
 "escalate":true
}
```

instead of hidden inside natural language.

---

### UI integration

Confidence, escalation reason and workflow stage can appear directly in the dashboard.

---

## Why inject SOP at runtime?

The SOP is inserted into every model call.

Benefits:

- Updated prices require no retraining
- New services become available immediately
- Grounding boundaries remain explicit
- Reduces hallucination risk

The model should only know what exists inside `sop.json`.

---

# 3. Hallucination Prevention

The workflow uses multiple safety layers.

---

## Layer 1 — Prompt restrictions

Prompt explicitly states:

> Answer ONLY from SOP  
> Do NOT invent information

Strong negative instructions discourage unsupported claims.

---

## Layer 2 — SOP gap detection

Unsupported questions trigger:

```json
{
"sop_gap": true
}
```

The gap is:

- displayed in UI
- stored in state
- added to escalation tracking

---

## Layer 3 — Consecutive unanswered threshold

If:

```txt
unanswered_count >= 2
```

workflow escalates automatically.

This acts independently of model judgement.

---

# 4. Confidence & Escalation Handling

The model returns:

```txt
confidence = 0.0–1.0
```

Confidence is displayed in UI for transparency.

Current escalation triggers:

| Trigger | Source | Action |
|---------|---------|---------|
| `escalate=true` | Model self-flag | Escalate |
| `sop_gap` repeatedly | Application threshold | Escalate |
| Angry sentiment | Keyword guard | Escalate before LLM |
| Explicit human request | Keyword guard | Escalate before LLM |

Examples:

```txt
I am furious
```

↓

Escalate

---

```txt
I want to speak to a manager
```

↓

Escalate

---

Future iterations could use low confidence scores as an additional escalation signal.

---

# 5. Tone & Persona Design

Assistant name:

```txt
Bloom
```

Chosen to match clinic branding.

Persona goals:

### Receptionist, not chatbot

Responses should feel:

- polite
- brief
- warm
- professional

rather than robotic.

---

### Non-medical behaviour

Prompt discourages medical advice.

Unsafe questions should be escalated.

---

### Concise responses

Customers usually want:

- pricing
- availability
- booking info

Responses avoid long explanations.

---

# 6. Lead Qualification Design

Lead qualification currently uses **predefined structured questions** rather than fully prompt-driven generation.

Questions collected:

1. Treatment interest
2. Previous experience
3. Booking readiness

Reason:

Fixed questions guarantee consistent data collection across sessions.

A separate `QUALIFY_PROMPT` exists as an extension point for future iterations.

---

# 7. LangGraph Architecture

Workflow execution is **state-driven**.

```txt
User Message
      ↓
Router
(checks current state["stage"])
      ↓

faq_node
qualify_node
escalation_node
summary_node

      ↓

Node updates AgentState

      ↓

Router selects next node
```

---

Current stages:

```txt
faq
qualify
escalated
summary
```

State stores:

- messages
- qualification answers
- SOP gaps
- escalation reason
- workflow stage
- session status

---

## Why LangGraph?

LangGraph was chosen because:

- workflow stages are explicit
- routing is deterministic
- debugging is easier
- state persists across nodes
- new stages can be added without rewriting logic

---

# 8. Summary Generation Design

At conversation end, a separate prompt generates:

- customer intent
- qualification data
- SOP gaps
- recommended next action

Output is saved as:

```txt
summary_<session_id>.json
```

This provides structured handoff information for human teams.

---

# 9. Trade-offs & Limitations

| Limitation | Notes |
|------------|-------|
| Keyword sentiment detection | Fast but misses nuance |
| Static SOP | Supports one business only |
| No DB persistence | Sessions reset on restart |
| No auth | Out of scope |
| No streaming responses | Full responses returned |
| Summary generated once | Production systems may update continuously |

---

# 10. Future Improvements

Possible production upgrades:

- Redis/Postgres session storage
- LLM-based sentiment classification
- Dynamic SOP management
- Appointment booking workflows
- Streaming responses
- Confidence-based automatic escalation