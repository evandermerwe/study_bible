# Study Bible

A New Church / Swedenborgian study Bible, typeset with [OpTeX](https://petr.olsak.net/optex/) and [OpBible](http://opbible.org) for physical publication.

The document driver is `main.tex`. Building it requires LuaTeX and OpTeX, with the macros in `opbible/macros` on TeX's input path.

## License

Copyright in the study notes, introductions, formatting, and articles belongs to Eric van der Merwe. That original work is licensed under the MIT License. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

Other material keeps its own license:

| Material | License |
| --- | --- |
| `notes/`, `intros/`, `formats/`, `articles/`, `main.tex`, `bible_text/convert_to_txs.py` | Copyright (c) 2026 Eric van der Merwe, MIT |
| `opbible/` and `books.tex` | GNU General Public License, version 2 |
| `bible_text/luke_kjv.txt`, `bible_text/rev_kjv.txt` | Project Gutenberg License, included in each file |
| `bible_text/KJV-*.txs` | King James Version text, public domain in the United States |

## Contributing

Changes are made by pull request. Eric van der Merwe is the only person who can approve a pull request, and a pull request is required before anything is merged into `main`. See [CONTRIBUTING.md](CONTRIBUTING.md).
