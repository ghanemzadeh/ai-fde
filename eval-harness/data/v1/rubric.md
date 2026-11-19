# Rubric v1: contract redline memo

Written for the people who label examples. It follows the worked example in Appendix A.8 of *Forward Deployed AI Engineering*. The playbook it refers to is [playbook.md](playbook.md).

Owner: [the customer's reviewing lawyer]
Version: v1. A change to this rubric needs a new eval-set version (a new folder, `data/v2`).

## C1. Clause coverage

The memo identifies every clause that diverges from the playbook.

Score: 1 if every divergent clause is surfaced, 0 if any is missed.
Weight: 40 percent. This is the criterion that carries the most weight.

## C2. Risk accuracy

For each surfaced clause, the memo gives the risk as high, medium or low, as the playbook does.

Score: the fraction correct, between 0 and 1. Clauses marked material in the playbook count double.
Weight: 30 percent.

## C3. Citation correctness

Every claim in the memo cites the section of the contract it refers to, and the section number resolves to the correct text.

Score: the fraction of citations that resolve correctly, between 0 and 1.
Weight: 15 percent.

## C4. Attorney usability

The memo is ordered by risk priority, uses plain language, and is under 600 words.

Score: 1 if all five answers are yes, otherwise 0.

- Is the priority order correct?
- Is it free of legalese, except where it quotes the contract?
- Is it under 600 words?
- Is it free of hedging language, such as "may be a concern"?
- Does every claim tie to a specific section, with no invented clauses?

Weight: 15 percent.

## Hard fails

These fail the case whatever the other scores are.

- Missing a clause marked material in the playbook.
- Describing a clause that is not in the contract.
- Citing a section that does not exist.

## Aggregation

Score out of 100 = 40 × C1 + 30 × C2 + 15 × C3 + 15 × C4.

The system clears validation when the average score across the eval set is 80 or more and no case has a hard fail.
