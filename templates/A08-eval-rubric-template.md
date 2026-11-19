# Eval Rubric Template

From *Forward Deployed AI Engineering* by Nasser Ghanemzadeh — Appendix A.8; see Chapter 9.

The rubric template below is the one I draft in the first week of validation, before the eval set has any cases in it. Writing the rubric before grading the first example is what forces the team and the customer to agree, in writing, on what *good* means.

```
EVAL RUBRIC v1 — [engagement name]
====================================

Owner: [name; customer's domain expert if possible]
Date drafted: [date]
Sign-off: [sponsor signature]

PURPOSE
  This rubric defines what good output looks like for the
  [system name]. Each criterion below is scored
  independently. The hard-fail rules at the bottom apply
  regardless of other scores.

C1. [Primary criterion — the one the customer cares most
     about, named in the customer's terms]
  Description: [What this measures, in plain language.]
  Score: [Continuous or categorical. If categorical, list
    the categories with their definitions.]
  Weight: [Relative weight in the aggregate score, if
    aggregated.]

C2. [Secondary criterion]
  Description: ...
  Score: ...
  Weight: ...

C3. [Tertiary criterion]
  Description: ...
  Score: ...
  Weight: ...

C4. [Usability or format criterion, if relevant]
  Description: ...
  Score: ...
  Weight: ...

HARD FAILS
  The following conditions are hard fails regardless of
  other scores:
    - [Specific condition, e.g., a missing material clause]
    - [Specific condition]
    - [Specific condition]

AGGREGATION
  The system's overall score on this rubric is calculated
  as: [explicit formula or rule].

  The system clears validation when its aggregate score
  on the eval set is at least [X] and no hard fails occur
  on cases marked as [criticality flag].
```

A filled-in version is in [A08-eval-rubric-worked-example.md](A08-eval-rubric-worked-example.md).
