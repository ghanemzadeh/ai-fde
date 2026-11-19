# Contributing

This repository holds the companion material for *Forward Deployed AI Engineering*. Corrections are welcome.

## Report an error in the book

Open an [erratum issue](https://github.com/ghanemzadeh/ai-fde/issues/new?template=erratum.yml). Give the chapter or appendix section, the sentence as printed, and what you think it should say. A source helps.

## Report a broken link

The reference list was checked when the book went to press, and pages move. Open an issue with the reference number and, if you have it, the new address.

## Fix the code

Pull requests for `eval-harness/` are welcome. Before you open one:

```bash
cd eval-harness
pip install -r requirements.txt
python -m pytest
```

Keep the harness small. It is meant to be read in one sitting and adapted, so a change that adds a dependency or a framework will probably be declined.

## The templates

The templates match the printed book, so wording changes are handled as errata. If you have adapted a template and it worked well for you, an issue describing what you changed is useful to other readers.
