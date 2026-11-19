# First-Slice Repository Layout

From *Forward Deployed AI Engineering* by Nasser Ghanemzadeh — Chapter 10.

> The layout of a first slice: three Python files, three prompts, an eval suite and a traces folder. No agent framework, no orchestration library, no vector store.

```
/contract-review-v1
  README.md              — one page: how to run it, what it does
  /prompts
    pre_scan.md          — the section-listing pre-pass prompt
    redline.md           — the main redline-memo prompt
    playbook.md          — the firm's standard playbook,
                           lightly reformatted from the
                           customer's Word doc
  /src
    main.py              — receive a contract, call models,
                           return a memo. Sixty lines.
    parse.py             — pull text from PDF or Word; section
                           detection; appendix detection. About
                           a hundred and forty lines, the
                           dominant complexity in the slice.
    format.py            — turn the model's structured output
                           into the memo format the firm uses.
                           Forty lines.
  /evals
    (the eval suite from Chapter 9, linked here as a git
    submodule so improvements flow both ways)
  /traces
    (per-run JSON dumps for the per-trace loop)
```
