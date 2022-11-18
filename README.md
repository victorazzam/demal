# demal
MAL (Meta Attack Language) to JSON decoding library and command-line tool.

## Info

**Author:** Victor Azzam

**License:** MIT

**Latest version:** `1.1.0`

**Requires:** Python 3.8 or later

**Batteries included:** Tests and examples are provided in this repository.

## Usage

### General usage
![usage.jpg](usage.jpg)

### Convert `file.mal` to `file.mal.json`
```shell
~ python demal.py file.mal
```

### Convert `file.mal` to `output.json`
```shell
~ python demal.py file.mal output.json
```

### Convert `file.mal` and print it out
```shell
~ python demal.py file.mal -
```

### Read from standard input, convert, and print it out
```shell
~ cat file.mal | python demal.py - -
```

### Read from standard input, convert, and write to `out.json`
```shell
~ cat file.mal | python demal.py - out.json
```

### Convert several files and view them interactively
```shell
~ cat file1.mal file2.mal | python demal.py - - | less
```

### Display debugging information while converting
```shell
~ python demal.py test1.mal debug
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
# output truncated
```

### Use it as a Python module
```py
from demal import MalParser
mal = MalParser('threat-model.mal')
mal.debug = True
mal.parse() # displays debugging messages due to the previous line
# output suppressed

mal.dump(out='parsed.json', pretty=True) # beautify and save to parsed.json
print(mal) # pretty-prints the json object
{
  "associations": {
    "Connection": {
      "asset_l": "Server",
      "asset_l": "Client",
# output truncated
```

#### Merge multiple instances by addition (also multiplication and bitwise-or)
Check `test.py`:
```py
import json
from demal import MalParser

print('Parsing two test files and combining their results.')
m1, m2 = MalParser('test1.mal'), MalParser('test2.mal')
m1.parse() ; m2.parse()

print('First:', m1['version'])
# First: 1.0.0

print('Second:', m2['version'])
# Second: 0.0.0

m = m1 + m2 # combine category/association items, same as "include"
print('Combined:', m['version'])
# Combined: 0.0.0

print('\nModifying a single variable.')
v = {'version': '1.3.3.7'}
m += v
print('New version:', m['version'])
# New version: 1.3.3.7

print('\nChanging inner dictionary data.')
var = m['categories']['System']['assets']['Host']['attributes']['guessedPassword']['probability']
print('Before:', var)
# Before: Exponential(0.02)

var = 'abc' # directly modify data
print('After:', var)
# After: abc

print('\nListing all categories, associations, and major keys/variables.')
print(list(m))
# ['id', 'version', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'System', 'A', 'Credentials', 'I2', 'I5', 'NetworkAccess']
```

## Output

This program produces the following approximate output:

```py
{
  "associations": {
	"Association": {
	  "asset_l": "left_asset",
	  "asset_r": "right_asset",
	  "field_l": "left_field",
	  "field_r": "right_field",
	  "meta": {
		"key": "value"
		# ...
	  },
	  "mult_l": "left_multiplier",
	  "mult_r": "right_multiplier"
	} # ...
  },
  "categories": {
	"Category1": {
	  "assets": {
		"Asset1": {
		  "abstract": false,
		  "attributes": {
			"access": {
			  "cia": null,
			  "meta": {},
			  "probability": "Exponential(0.02)", # etc, or simply null
			  "tags": [],
			  "type": "and"
			},
			"authenticate": {
			  "cia": null,
			  "leads_to": {
				"0": "access",
				"a": "b \\/ c " # result of: let a = ...
			  },
			  "meta": {},
			  "probability": null,
			  "tags": [
				"hidden",
				"debug",
				"trace"
			  ],
			  "type": "or"
			} # ...
		  },
		  "extends": null,
		  "meta": {}
		} # ...
	  },
	  "meta": {}
	}
  },
  "id": "org.name.project",
  "version": "1.0.0"
}
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
 - **Guide:** [https://nse.digital/...](https://nse.digital/pages/guides/Creating%20threat%20models/MAL.html)
 - **MAL author video:** [https://play.kth.se/...](https://play.kth.se/media/t/0_ckc2056q)
 - **Project page:** [https://www.kth.se/...](https://www.kth.se/cs/nse/research/software-systems-architecture-and-security/projects/mal-the-meta-attack-language-1.922174)
 - **Research paper:** [https://dl.acm.org/doi/10.1145/3230833.3232799](https://dl.acm.org/doi/10.1145/3230833.3232799)
 
