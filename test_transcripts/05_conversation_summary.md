# Test Transcript 5 — Full Conversation Summary
# Scenario: End-to-end session → structured summary generated.

---

[Full session condensed]

User:  What are your filler prices?
Bloom: Our dermal fillers start from £250. The final cost depends on the
       area and volume required, which we'd go over in your free consultation.

User:  Do you do nose fillers?
Bloom: I don't have specific information about nose fillers in my current
       data. I'd recommend checking with our team directly to confirm.
       [SOP Gap logged]

User:  Okay that's fine. What treatments are you most interested in?
       [Stage transitions to: ✅ Lead Qualification]

Bloom: Great! To help our team prepare for you — what type of treatment
       are you most interested in? Botox, Fillers, or a Consultation?

User:  Fillers for my cheeks.
Bloom: Lovely! Have you had aesthetic treatments before, or would this
       be your first time?

User:  I've had Botox once before.
Bloom: Wonderful! Last question — are you looking to book soon, or still
       researching?

User:  Ready to book, maybe this weekend.
Bloom: Perfect! Here's what I've noted: cheek fillers, experienced patient,
       ready to book this weekend. I'd suggest booking your consultation via
       WhatsApp or the website. [stage_complete: true]

[User types: quit]
[Summary generation triggered]

---

📊 GENERATED SUMMARY (saved to summary_a3f1b2c4.json):

{
  "session_id": "a3f1b2c4-...",
  "timestamp": "2026-05-23T11:02:44Z",
  "customer_intent": "Customer is interested in cheek dermal fillers and is ready to book an appointment this weekend.",
  "key_details_collected": {
    "treatment_interest": "Cheek fillers",
    "experience_level": "Experienced — has had Botox previously",
    "booking_readiness": "Ready to book this weekend"
  },
  "sop_gaps": [
    "Do you do nose fillers?"
  ],
  "recommended_next_action": "Priority follow-up — high-intent lead. Book consultation ASAP. Also clarify nose filler availability in SOP for future.",
  "escalated": false,
  "escalation_reason": null
}

---

RESULT: ✅ PASS — Summary correctly captured intent, qualification answers,
        SOP gaps, and recommended next action. Saved to timestamped JSON file.
