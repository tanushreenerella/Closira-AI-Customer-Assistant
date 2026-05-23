# Test Transcript 3 — Escalation Trigger (Angry Sentiment)
# Scenario: Customer expresses frustration → AI detects sentiment and hands off.

---

User:  Hi, I had a consultation last week and the results were absolutely
       terrible. I'm furious and this is completely unacceptable. I want
       someone to fix this now.

[PRE-FLIGHT SENTIMENT CHECK → TRIGGERED]
[Keyword detected: "furious", "terrible", "unacceptable"]
[Escalation reason: Angry sentiment detected: 'furious']
[Logged to escalation_log.json immediately — before Claude is even called]

Bloom: I'm really sorry to hear you're feeling this way. I'm going to
       connect you with one of our team members right away so they can
       assist you properly. 💐

       [Escalate: true] [Confidence: 1.0]
       [Escalation reason: Angry sentiment detected: 'furious']

---

🔴 ESCALATED — Conversation snapshot saved to escalation_log.json
   Timestamp: 2026-05-23T10:14:22Z
   Session: a3f1b2c4…

RESULT: ✅ PASS — Sentiment detected via pre-flight keyword guard BEFORE Claude
        was called. Escalation was immediate, warm, and logged with full context.
        No attempt was made to handle a complaint the AI is not equipped for.
