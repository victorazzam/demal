'''
Mal-lang (https://mal-lang.org) parser.
Author: Victor Azzam
Version: 1.0.0

Limitations:
 [-] Quotation marks must not be escaped.
 [-] Expects clean spec-compliant code.
'''

import re, sys, json, inspect

class MalParser:
    '''
    Mal language parser that converts .mal files into JSON data.
    Spec: https://github.com/mal-lang/malcompiler/wiki/MAL-language-specification
    Syntax: https://github.com/mal-lang/mal-documentation/wiki/MAL-Syntax
    Reference: malcompiler-lib/src/main/java/org/mal_lang/compiler/lib/Lexer.java
    Guide: https://nse.digital/pages/guides/Creating%20threat%20models/MAL.html
    Mal author video: https://play.kth.se/media/t/0_ckc2056q
    '''

    def __init__(self, file):
        self.src = file
        self.result = {}

    def __repr__(self):
        '''
        Define
        '''
        return json.dumps(self.result, sort_keys=True, indent=2)

    def dump_json(self, out = None, pretty = True):
        '''
        Output a JSON file with the results.
        '''
        pretty = pretty is True
        out = out if out else f'{self.src}.json'
        with open(out, 'w') as f:
            json.dump(self.result, f, sort_keys = pretty, indent = 2 * pretty)

    @staticmethod
    def iterate(file):
        '''
        Iterate a file line by line.
        '''
        try:
            with open(file) as f:
                data = f.read()

                # Remove comments.
                # https://codegolf.stackexchange.com/a/48346/79525 :D
                regex = r'("[^\n]*"(?!\\))|(//[^\n]*$|/(?!\\)\*[\s\S]*?\*(?!\\)/)'
                for comment in re.findall(regex, data, 8):
                    data = data.replace(comment[1], '')

                # Yield non-empty lines.
                for line in data.splitlines():
                    if line.strip():
                        if globals().get('debug') == True:
                            print(inspect.stack()[1].function, 'got:\x1b[92;1m', repr(line.strip()), '\x1b[m')
                        yield line.strip()
        except IOError:
            quit(f'Error while opening {file}')

    def parse(self, file = None):
        '''
        Parses individual files, recursively evaluating imports (includes).
        '''
        file = file if file else self.src
        code = self.iterate(file)

        # Regular expressions for the main declarations
        #r_end = r'\s*(//.*)?$' # for inline comments
        r_define = re.compile(r'#(\w+):\s*"([^"]*)"')
        r_include = re.compile(r'include "([^"]*)"')
        r_category = re.compile(r'category \w+')
        r_associations = re.compile(r'associations\s*\{$')

        # Parse each line
        try:
            for line in code:
                if (r := r_define.match(line)):
                    self.result[r.group(1)] = r.group(2)
                elif (r := r_include.match(line)):
                    self.parse(r.group(1))
                elif r_category.match(line):
                    self.parse_category(code, line)
                elif r_associations.match(line):
                    self.parse_associations(code, line)
                else:
                    quit(f'Improper syntax: {repr(line)}')
        except StopIteration:
            quit(f'Incomplete script at:\n {repr(line)}')
        #except Exception as e:
        #    quit(f'Error at: {repr(line)}\nMessage: {e}')

    def parse_header(self, code, line, cat=None):
        '''
        Parse category or asset section header.
        '''
        r_asset = re.compile(r'(abstract )?asset (\w+)( extends (\w+))?')
        r_cat = re.compile(r'category (\w+)')
        r_meta = re.compile(r'([\w ]+):\s+"(.*)"')

        # Name and possible asset inheritance options
        if (r := r_asset.match(line)):
            abstract, name, _, extends = r.groups()
            section = cat['assets'][name] = {
                'meta': {},
                'attributes': {},
                'extends': extends,
                'abstract': abstract is not None
            }
        elif (r := r_cat.match(line)):
            if 'categories' not in self.result:
                self.result['categories'] = {}
            section = self.result['categories'][r.group(1)] = {
                'meta': {},
                'assets': {}
            }
        else:
            quit(f'Improper syntax: {repr(line)}')

        # Metadata
        if '{' not in line:
            while '{' not in (line := next(code)):
                if (r := r_meta.match(line)):
                    section['meta'][r.group(1)] = r.group(2)

        # Reference to the whole section
        return section

    def parse_asset(self, code, asset):
        '''
        Parse an asset body.

        Sym      Meaning
        ---      -------
        |        logical or (attack)
        &        logical and (attack)
        #        protection mechanism (defense)
        +>       append
        ->       leads to
        <-       requires
        *        star
        /\       intersection
        \/       union
        E        exists
        !E       does not exist (lacks)
        X.A      collect (asset X's attack step A)
        X*.A     transitive, e.g. dir.subdir.subdir.file can be dir*.file
        [prob]   probability distribution, one of:
                    Bernoulli(p)
                    Binomial(n, p)
                    Exponential(λ)
                    Gamma(k, θ)
                    LogNormal(μ, σ)
                    Pareto(x, α)
                    TruncatedNormal(μ, σ^2)
                    Uniform(a, b)
        {C,I,A}  (securiCAD only) confidentiality, integrity, availability (any combination)
        @hidden  (securiCAD only) hide from attack paths
        @debug   (securiCAD only) show only while testing
        @trace   (securiCAD only) trace intermediary steps, e.g. userAccount.assume->action.perform
        '''
        r_attr = re.compile(r'([|&#E]{1}|[!E]{2})\s+(\w+)(\s+\[([\w(). ,]+)\])?')
        r_cia = re.compile(r'{\s*([CIA])(,\s*([CIA])(,\s*([CIA]))?)?\s*}')
        r_meta = re.compile(r'([\w ]+):\s+"(.*)"')
        kinds = dict(zip('| & # E !E'.split(), 'or and defense exists lacks'.split()))
        sym = dict(zip('+> -> <-'.split(), 'append leads_to require'.split()))
        last_attr = None

        while '}' not in (line := next(code)):
            if (r := r_attr.match(line)) and r.group(1) in kinds:
                kind, name, _, prob = r.groups()
                cia = r_cia.search(line)
                last_attr = asset[name] = {
                    'meta': {},
                    'type': kinds[kind],
                    'probability': prob,
                    'cia': sorted(set(cia.groups()[::2]), key='CIA'.find) if cia else None,
                    'tags': [x[1:] for x in line.split() if x in ('@hidden', '@debug', '@trace')]
                }
            elif (r := r_meta.match(line)) and last_attr:
                last_attr['meta'][r.group(1)] = r.group(2)
            elif (pre := line.split()[0]) in sym:
                field = last_attr[sym[pre]] = {}
                line = line[2 + (not line[0].isalpha()):]
                self.parse_expression(code, line, field)
            else:
                quit(f'Improper syntax: {repr(line)}')

    def parse_expression(self, code, line, field):
        r_let = re.compile(r'let ([A-Za-z_]\w*)\s*=\s*"?([^"]+)"?')
        i = 0
        while 1:
            if (r := r_let.match(line)):
                name, value = r.groups()
            else:
                name, value, i = (i, line, i+1)
            field[str(name)] = [value.rstrip(',')]
            if not line.endswith(','):
                break
            line = next(code)

    def parse_category(self, code, line):
        '''
        Parse the category directive.
        '''
        category = self.parse_header(code, line)
        while '}' not in (line := next(code)):
            asset = self.parse_header(code, line, category)
            self.parse_asset(code, asset['attributes'])

    def parse_associations(self, code, line):
        '''
        Parse the association directive.
        '''
        r_association = re.compile(r'(\w+)\s+\[(\w+)\]\s+([\d*.]+)\s+<--\s+(\w+)\s+-->\s+([\d*.]+)\s+\[(\w+)\]\s+(\w+)')
        r_meta = re.compile(r'([\w ]+):\s+"(.*)"')
        last_link = None

        while '}' not in (line := next(code)):
            if (r := r_association.match(line)):
                asset_l, field_l, mult_l, link, mult_r, field_r, asset_r = r.groups()
                if 'associations' not in self.result:
                    self.result['associations'] = {}
                last_link = self.result['associations'][link] = {
                    'asset_l': asset_l,  'asset_r': asset_r,
                    'field_l': field_l,  'field_r': field_r,
                    'mult_l' : mult_l,   'mult_r' : mult_r,
                    'meta': {}
                }
            elif (r := r_meta.match(line)) and last_link:
                last_link['meta'][r.group(1)] = r.group(2)

def main(f, out):
    mal = MalParser(f)
    mal.parse()
    if out == '-':
        print(mal)
    else:
        mal.dump_json(out=out, pretty=True)

def quit(msg='Exiting.'):
    print(msg, file=sys.stderr, flush=True)
    sys.exit()

if __name__ == '__main__':
    try:
        args = sys.argv
        debug = 'debug' in args
        if len(args) < 2 or not args[1].lower().endswith('.mal'):
            quit(f'Usage: {args[0]} file.mal [output.json] [debug]')
        output = args[2] if len(args) > 2 and (args[2].lower().endswith('.json') or args[2] == '-') else None
        main(args[1], output)
    except (KeyboardInterrupt, EOFError):
        print('\nInterrupted.')