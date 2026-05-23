# Test Transcript 4 — Lead Qualification
# Scenario: AI asks 3 structured questions and produces a qualification summary.

---

[After initial FAQ exchange, stage transitions to: ✅ Lead Qualification]

Bloom: Lovely! Before I help you take the next step, I'd love to learn
       a little more about what you're looking for. What type of treatment
       are you most interested in — Botox, Fillers, or starting with a
       free Consultation?

       [Stage: qualify] [Confidence: 0.97]

---

User:  I'm thinking fillers, maybe for my lips.

Bloom: Wonderful — lip fillers are one of our most popular treatments!
       My next question: have you had any aesthetic treatments before,
       or would this be your first time?

       [Stage: qualify] [Confidence: 0.96]
       [Qualification collected → answer_1: "I'm thinking fillers, maybe for my lips."]

---

User:  First time, yes. A little nervous about it.

Bloom: That's completely understandable — it's very normal to feel that
       way before a first treatment! Our practitioners are very gentle and
       will walk you through everything. Last question: are you looking to
       book an appointment soon, or are you still in the research phase?

       [Stage: qualify] [Confidence: 0.95]
       [Qualification collected → answer_2: "First time, yes. A little nervous about it."]

---

User:  I'd love to book something in the next couple of weeks.

Bloom: That's great to hear! Here's a quick summary of what I've noted
       for our team:
       • Treatment interest: Lip fillers
       • Experience: First-time patient
       • Booking timeline: Next 2 weeks

       I'd recommend starting with our free consultation so you can meet
       the practitioner and discuss your goals before committing. You can
       book via WhatsApp or our website. Shall I help with anything else?

       [Stage: summary] [stage_complete: true]
       [Qualification collected → answer_3: "I'd love to book something in the next couple of weeks."]

---

RESULT: ✅ PASS — AI asked all 3 qualification questions one at a time,
        collected answers cleanly, produced a warm summary, and transitioned
        to the summary stage correctly.
