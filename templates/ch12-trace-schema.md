# Minimum Telemetry Trace Schema

From *Forward Deployed AI Engineering* by Nasser Ghanemzadeh — Chapter 12.

> Ten fields to log on every trace, from the first commit.

- *trace_id* — the per-request identifier that ties every log line in a request together
- *agent_id* and *agent_version* — the identity from Chapter 11, plus the version of the prompt/configuration in effect
- *input* — the customer-facing input, with any PII handling the governance layer requires
- *model* and *model_version* — the underlying model, with the date the version was pinned
- *prompt_hash* — the hash of the prompt template in use, for fast lookup against the prompt store
- *tool_calls* — for each tool invocation, the name, arguments, result, and latency
- *output* — the final output the system returned to the customer
- *eval_score* — if the trace was graded by an inline judge or sampled for human review, the score
- *human_intervention* — the place in the flow where a human approved, edited, or escalated
- *cost* — the token cost of the trace, summed across all model calls

As a JSON skeleton:

```json
{
  "trace_id": "",
  "agent_id": "",
  "agent_version": "",
  "input": "",
  "model": "",
  "model_version": "",
  "prompt_hash": "",
  "tool_calls": [
    {"name": "", "arguments": {}, "result": "", "latency_ms": 0}
  ],
  "output": "",
  "eval_score": null,
  "human_intervention": null,
  "cost": 0.0
}
```
