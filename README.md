# demal
MAL (Meta Attack Language) to JSON decoder

## [Mal-lang](https://mal-lang.org) parser.

**Author:** Victor Azzam

**Latest version:** `1.0.0`

**Requires:** Python 3.6 or later

Test files and their output are included in this repository.

## Usage

Convert `file.mal` to `file.mal.json`:
```shell
~ python demal.py file.mal
```

Convert `file.mal` to `output.json`:
```shell
~ python demal.py file.mal output.json
```

Display debug information while converting:
```shell
~ python demal.py test1.mal debug
```
```
parse got: '#id: "tmp"'
parse got: '#version: "0.0.0"'
parse got: 'category C1 {'
parse_category got: '}'
parse got: 'category C2'
parse_header got: 'user info: "info"'
parse_header got: '{'
parse_category got: 'asset A1 {'
parse_asset got: '& At1'
parse_asset got: '| At2'
...
```

You can also use it as a library within a Python script:
```py
from demal import MalParser
mal = MalParser('threat-model.mal')
debug = True
mal.parse() # displays debugging messages (if enabled)
mal.dump_json(out='parsed.json', pretty=True) # beautify and save to parsed.json
print(mal) # pretty-prints the json object
```
```
{
  "associations": {
    "Connection": {
      "asset_l": "Server",
      "asset_l": "Client",
...
```

## Limitations
 - [X] ~Multi-line comments should be avoided.~
 - [ ] Quotation marks must not be escaped.
 - [ ] Expects clean spec-compliant code.

## Resources
 - **Example:** [exampleLang/src/main/mal/exampleLang.mal](https://github.com/mal-lang/exampleLang/blob/master/src/main/mal/exampleLang.mal)
 - **Spec:** [malcompiler/wiki/MAL-language-specification](https://github.com/mal-lang/malcompiler/wiki/MAL-language-specification)
 - **Syntax:** [mal-documentation/wiki/MAL-Syntax](https://github.com/mal-lang/mal-documentation/wiki/MAL-Syntax)
 - **Reference:** [malcompiler-lib/src/main/java/org/mal_lang/compiler/lib/Lexer.java](https://github.com/mal-lang/malcompiler/blob/master/malcompiler-lib/src/main/java/org/mal_lang/compiler/lib/Lexer.java)
 - **Guide:** [https://nse.digital/pages/guides/Creating%20threat%20models/MAL.html](https://nse.digital/pages/guides/Creating%20threat%20models/MAL.html)
 - **MAL author video:** [https://play.kth.se/media/t/0_ckc2056q](https://play.kth.se/media/t/0_ckc2056q)
