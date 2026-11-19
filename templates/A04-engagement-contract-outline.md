# Engagement Contract Outline

From *Forward Deployed AI Engineering* by Nasser Ghanemzadeh — Appendix A.4; see Chapters 17 and 20.

> This outline is a starting point for a negotiation. It is not legal advice. Have a lawyer review any agreement before you sign it.

A template for an engagement-shaped FDE deal in the $250,000–$2 million annual range. Larger contracts will require more sophisticated legal handling; smaller ones can use this directly. A starting point for the negotiation, not a final document.

```
ENGAGEMENT AGREEMENT — OUTLINE

PARTIES
  Vendor: [Name]
  Customer: [Name, billing entity]

ENGAGEMENT SCOPE
  Per the scoping document attached as Schedule A, signed by both
  parties on [date].

DELIVERABLES AND MILESTONES
  Milestone 1 — Scoping: [Amount, due on signature]
    Deliverable: signed scoping document.
  Milestone 2 — Validation: [Amount, due on threshold clear]
    Deliverable: eval-set results clearing the agreed threshold.
  Milestone 3 — Delivery: [Amount, due on production deployment]
    Deliverable: production system live; runbook delivered.
  Milestone 4 — Outcome: [Amount, due on metric movement]
    Deliverable: customer-confirmed movement of the success metric
    over the agreed measurement window.

ONGOING CONSUMPTION (optional)
  Beyond milestones, the customer will pay [$X per unit] for ongoing
  system operation, billed monthly, with a minimum monthly fee of [$Y].

CHANGE CONTROL
  Material changes to scope require a written amendment signed by
  both the vendor lead and the customer sponsor. Amendments do not
  require legal re-approval if they fit within [+/-N%] of the
  original budget.

EARLY TERMINATION
  Either party may terminate this agreement on [N] days written
  notice if the validation threshold is not cleared within the
  validation window. In the event of early termination, the customer
  pays only for milestones already achieved. Neither party owes
  penalties for early termination under this clause.

IP AND CODE OWNERSHIP
  Customer-specific code: owned by the customer.
  Generalized patterns, eval frameworks, and infrastructure
    contributions: owned by the vendor.
  The vendor retains the right to use lessons learned from this
  engagement to improve the vendor's product. The customer's data
  is not used for any purpose other than this engagement without
  separate written agreement.

GOVERNANCE
  The vendor will operate within the customer's standard SOC 2,
  HIPAA, and EU AI Act compliance requirements as applicable.
  Specific controls and evidence requirements are listed in
  Schedule B.
```
