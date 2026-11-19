# Portfolio Repository README Template

From *Forward Deployed AI Engineering* by Nasser Ghanemzadeh — Appendix A.10; see Chapter 14.

The README template for a portfolio project, in the order Chapter 14 recommended. The order matters; the forty-five-second test runs from the top.

````
# [project name in plain language]

[One sentence describing what the project does, in the
customer's terms. "An invoice-triage assistant that
sorts and categorizes inbound documents for a small
accounting practice," not "A multi-modal LLM pipeline."]

## Impact

[One paragraph. Customer (real or named), baseline,
result, time window. If the project is not yet
production-deployed, name that honestly and describe
the rigor of the evaluation: "Ran against 500 sampled
documents from a public dataset; correctly categorized
87% per the rubric in /evals."]

## Architecture

![architecture diagram](docs/architecture.png)

[One paragraph naming the components, the data flow,
the model, the eval suite, and the deployment surface.
Two minutes of reading.]

## How to run

```bash
git clone [repo]
cd [repo]
pip install -r requirements.txt
cp .env.example .env  # fill in your API key
python -m project.demo  # runs on sample data
python -m project.evals  # runs the eval suite
```

## Demo

[Two-minute screen recording. Embedded if possible,
linked otherwise. The voiceover is you, walking
through one input and the system's output.]

## Eval suite

See [/evals](./evals) for the rubric, the data, the
labeling protocol, and the version history. The
current pass rate is [X]%.

## Lessons learned / post-mortem

[The honest version. What worked, what did not, what
you would do differently. Two pages maximum. This is
the section hiring managers read for differentiation.]

## About the author

[Your name, your role, your contact, your other links.
Two sentences.]
````

The README is the portfolio piece. Spend time on it. Most candidates do not. The ones who do not, do not get the call.
