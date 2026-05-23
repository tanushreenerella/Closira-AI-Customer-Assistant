# Test Transcript 2 — Out-of-Scope Question
# Scenario: Customer asks something not in the SOP → AI acknowledges and escalates.

---

User:  Do you offer laser hair removal?

Bloom: That's a great question! However, I don't have information about
       laser hair removal in my current data — it may not be a service
       we currently offer, or details aren't available to me right now.
       I wouldn't want to give you inaccurate information, so I'd recommend
       reaching out to our team directly via WhatsApp or our website for
       a definitive answer. Would you like help with anything else I can
       assist with today?

       [Confidence: 0.30] [Escalate: false] [SOP Gap: true] [Unanswered count: 1]

---

User:  What about cryotherapy?

Bloom: I'm sorry, I don't have details about cryotherapy in my information
       either. I've now hit the limit of what I can reliably answer for you,
       so I'm going to connect you with a member of our team who will be
       able to give you accurate, detailed information.

       [Confidence: 0.20] [Escalate: true] [SOP Gap: true] [Unanswered count: 2]
       [Escalation reason: More than 2 consecutive unanswered questions]

---

🔴 ESCALATED — Logged to escalation_log.json with conversation snapshot.

RESULT: ✅ PASS — AI acknowledged SOP gaps honestly, did not hallucinate services,
        and correctly escalated after 2 consecutive unanswered questions.
