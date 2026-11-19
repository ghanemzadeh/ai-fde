# Scoping Document Template

From *Forward Deployed AI Engineering* by Nasser Ghanemzadeh — Appendix A.2; see Chapter 6.

The scoping document is one page. The discipline of fitting it on one page is itself a forcing function — anything that does not fit is not yet clear enough to commit to.

```
ENGAGEMENT SCOPING DOCUMENT

Customer: [Company name, business unit]
Vendor lead: [FDE name, title]
Customer sponsor: [Name, title, exception-granting authority confirmed: Y/N]
Date drafted: [Date]
Date sponsor-approved: [Date]

PROBLEM STATEMENT
[Two sentences, in the customer's own words. What is broken today,
and what does the customer want to be true at the end of the engagement.]

TOP-FIVE-PRIORITIES CHECK
This engagement addresses the following item on the CEO's stated
top-five priorities for the year: [item, with sponsor confirmation].

SUCCESS METRIC
The metric this engagement will be judged on:
  [Metric name, in customer's units, with current baseline and
  desired direction.]
The metric will be measured by:
  [Specific data source, with refresh cadence.]

VALIDATION THRESHOLD
The eval set produced in week 2-3 will grade the proposed system
against [N] cases drawn from real customer data. The system must
score [X]% to clear the threshold and proceed to delivery.

FIRST-SLICE SCOPE (3 weeks)
The first slice will:
  - [End-to-end behavior in one sentence]
  - [Specific input format]
  - [Specific output format]
  - [Integration points: data sources read, systems written]
The first slice will NOT (deferred to future scope):
  - [Explicitly out-of-scope behaviors]

EXCEPTION-GRANTING PATH
For data access, identity provisioning, or governance review that
falls outside standard process, the sponsor has authorized the
following escalation path: [Names, with roles.]

CONTRACT STRUCTURE
  - Scoping fee (paid on signature): [$]
  - Validation milestone (paid on threshold-clear): [$]
  - Delivery milestone (paid on production deployment): [$]
  - Outcome milestone (paid on metric movement over [N] weeks): [$]

SIGN-OFF
  ___________________  ___________________
  Customer sponsor      Vendor lead
  Date:                 Date:
```
