# Test Transcript 1 — In-SOP Question
# Scenario: Customer asks about Botox pricing → AI answers accurately from SOP only.

---

User:  Hi, what are your Botox prices?

Bloom: Hi there! 🌸 Great question. Our Botox treatments start from £200.
       The exact price depends on the area(s) being treated and the amount
       of product required — we'd cover all of that in your free consultation.
       Would you like to book one?

       [Confidence: 95%] [Escalate: false] [SOP Gap: false]

---

User:  And how long does Botox last?

Bloom: Botox results typically last between 3 to 6 months. After that,
       most clients choose to come back for a top-up to maintain their results.
       Is there anything else you'd like to know?

       [Confidence: 98%] [Escalate: false] [SOP Gap: false]

---

RESULT: ✅ PASS — AI answered accurately from SOP without hallucinating any prices,
        durations, or additional services not present in the data.
