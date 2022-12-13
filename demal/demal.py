#!/usr/bin/env python3

'''
demal
-----
MAL (Meta Attack Language) to JSON encoding/decoding library and command-line tool.
'''

__version__ = '2.0.0'
__author__ = 'Victor Azzam'
__url__ = 'https://github.com/victorazzam/demal'

import os, io, re, sys, copy, json, inspect

# Check if the terminal supports styled output.
colors = 'win' not in sys.platform or any(os.getenv(x) is not None for x in ('WT_SESSION', 'WT_PROFILE_ID'))

# Red, green, yellow, blue, cyan, white, default.
r, g, y, b, c, w, z = (f'\x1b[{x}m' * colors for x in (91,92,93,94,96,97,0))

class MalParser:
    '''
    Mal language parser that converts .mal files into JSON data.
    '''

    def __init__(self, file, debug = False):
        '''
        Create new instance without parsing the MAL source file yet.
        '''
        self.src = file
        self.result = {}
        self.stop = True
        self.debug = debug

    def __repr__(self):
        '''
        Representation when referenced.
        '''
        return json.dumps(self.result, sort_keys=True, indent=2) + '\n'

    def __str__(self):
        '''
        String representation, minified.
        '''
        return json.dumps(self.result, sort_keys=True)

    def __add__(self, other):
        '''
        Handle: addition, multiplication, bitwise-or.
        The result will always be a union between both dictionaries.
        '''
        if isinstance(other, (dict, MalParser)):
            new = MalParser(self.src, self.debug)
            new.result = copy.deepcopy(self.result)
            newdata = copy.deepcopy(other if type(other) is dict else other.result)
            for key in newdata:
                n, newer = new.result.get(key), newdata[key]
                if type(n) == type(newer) == dict:
                    if key == 'categories' and all(type(y) is dict and 'assets' in y and 'meta' in y for x in (n, newer) for y in x):
                        for cat in n:
                            for i in ('assets', 'meta'):
                                n[cat][i].update(newer[cat][i])
                    else:
                        n.update(newer)
                else:
                    new.result[key] = newdata[key]
            return new
        raise SyntaxError(f'MalParser does not support combining with {type(other)} objects.')

    # Let __add__ handle + * | for consistency.
    __rmul__ = __mul__ = __ror__ = __or__ = __radd__ = __add__

    def __getitem__(self, item):
        '''
        Allow access to underlying result dictionary and conversion to dict type.
        '''
        return self.result.get(item)

    def __iter__(self):
        '''
        Allow iteration of assets using for loops.
        '''
        self.i = 0
        self.assets = []
        for cat in self.result.get('categories', []):
            category = self.result['categories'][cat]
            if type(category) is dict:
                for asset in sorted(category.get('assets', [])):
                    self.assets.append(f'{cat}.{asset}')
        return self

    def __next__(self):
        '''
        Allow iteration of assets using for loops.
        '''
        if self.i >= len(self.assets):
            del self.i, self.assets
            raise StopIteration
        self.i += 1
        return self.assets[self.i - 1]

    def quit(self, msg='Exiting.'):
        '''
        Handle exit message and stop parsing.
        '''
        print(msg, file=sys.stderr, flush=True)
        self.stop = True
        return 1

    def dump(self, out = None, pretty = True):
        '''
        Output a JSON file with the results.
        '''
        pretty = pretty is True
        output = 'output.mal.json'
        if type(out) is str and out:
            output = out
        elif out == sys.stdout:
            for i in (repr(self) if pretty else str(self)).splitlines():
                print(i)
            return
        elif type(self.src) is str:
            output = self.src + '.json'
        with io.open(output, 'w', newline='\n') as f:
            json.dump(self.result, f, sort_keys=pretty, indent=pretty*2)
            f.write('\n')

    def dump_mal(self, out = None):
        '''
        Generate a MAL file from the results dictionary.
        '''
        try:
            f = io.StringIO()
            f.write(f'// Output from demal v{__version__}\n')

            # Read strings first to keep them up top.
            for key, value in self.result.items():
                if type(value) is str:
                    f.write(f'\n#{key}: "{value}"')
            f.write('\n')

            # Then process the other objects.
            for key, value in self.result.items():
                if key == 'categories' and type(value) is dict:
                    for cname, category in value.items():
                        self._dump_category(f, cname, category)
                elif key == 'associations' and type(value) is list:
                    self._dump_associations(f, value)
                elif self.debug:
                    print(f'Unrecognized MAL pattern:', repr(key), ':', repr(value), file=sys.stderr, flush=True)
        except Exception:
            return self.quit('Current JSON configuration incompatible with MAL syntax.')

        # Output to file or terminal.
        f.seek(0)
        output = 'output.mal'
        if type(out) is str and out:
            output = out
        elif out == sys.stdout:
            for i in f.read().splitlines():
                print(i)
            return
        elif type(self.src) is str:
            output = self.src + '.mal'
        with io.open(output, 'w', newline='\n') as file:
            f.seek(0)
            file.write(f.read())

    @staticmethod
    def _dump_meta(obj, indent_level = 1):
        '''
        Metadata helper for generating MAL files.
        '''
        meta = []
        indent = '  ' * indent_level
        if type(obj) is dict and 'meta' in obj and type(obj['meta']) is dict:
            for key, value in obj['meta'].items():
                meta.append(f'{indent}{key}: "{value}"')
        return '\n'.join(meta)

    def _dump_category(self, f, cname, cat):
        '''
        Category helper for generating MAL files.
        '''
        meta = self._dump_meta(cat)
        f.write(f'\ncategory {cname}')
        f.write(f'\n{meta}\n{{\n' if meta else ' {\n')
        first = True
        for name, asset in cat['assets'].items():
            if not first:
                f.write('\n')
            first = False
            self._dump_asset(f, name, asset)
        f.write('}\n')

    def _dump_asset(self, f, name, asset):
        '''
        Asset helper for generating MAL files.
        '''
        meta = self._dump_meta(asset, 2)
        abstract = 'abstract ' if asset['abstract'] else ''
        extends = ' extends ' + asset['extends'] if asset['extends'] else ''
        f.write(f'  {abstract}asset {name}{extends}')
        f.write(f'\n{meta}\n  {{\n' if meta else ' {\n')

        kinds = dict(zip('or and defense exists lacks'.split(), '| & # E !E'.split()))
        sym = dict(zip('append leads_to require'.split(), '+> -> <-'.split()))
        for a_name, attr in asset['attributes'].items():
            # First line
            a = []
            if attr['probability']:
                a.append('[' + attr['probability'] + ']')
            if attr['cia']:
                a.append('{' + ','.join(attr['cia']) + '}')
            if attr['tags']:
                for tag in attr['tags']:
                    a.append('@' + tag)
            f.write(f'    {kinds[attr["type"]]} {a_name}' + (' ' if a else '') + ' '.join(a))

            # Possible metadata
            meta = self._dump_meta(attr, 3)
            f.write(f'\n{meta}\n' if meta else '\n')

            # Attributes
            for key in attr:
                if key in sym:
                    for i, expr in enumerate(attr[key].items()):
                        k, v = expr
                        expr = v if k.isdigit() else f'let {k} = {v}'
                        if i == 0:
                            f.write(f'{"":6}{sym[key]} {expr}')
                        else:
                            f.write(f',\n{"":9}{expr}')
                    f.write('\n')

        f.write('  }\n')

    def _dump_associations(self, f, associations):
        '''
        Association helper for generating MAL files.
        '''
        f.write('\nassociations {\n')
        for a in associations:
            f.write(f'  {a["asset_l"]} [{a["field_l"]}] {a["mult_l"]} <-- {a["name"]} --> {a["mult_r"]} [{a["field_r"]}] {a["asset_r"]}')
            meta = self._dump_meta(a, 2)
            f.write(f'\n{meta}\n' if meta else '\n')
        f.write('}\n')

    def iterate(self, file):
        '''
        Iterate a file line by line.
        '''
        try:
            file = file if file is sys.stdin else open(file)
            with file as f:
                data = f.read()

                # Remove comments.
                # https://codegolf.stackexchange.com/a/48346/79525 :D
                regex = r'("[^\n]*"(?!\\))|(//[^\n]*$|/(?!\\)\*[\s\S]*?\*(?!\\)/)'
                for comment in re.findall(regex, data, re.MULTILINE):
                    data = data.replace(comment[1], '')

                # Yield non-empty lines.
                for line in data.splitlines():
                    if not self.stop and (L := line.strip()):
                        if self.debug:
                            print(w + inspect.stack()[1].function, z + 'got:' + r, repr(L) + z, file=sys.stderr, flush=True)
                        yield L
        except BrokenPipeError:
            pass
        except IOError:
            self.quit(f'Error while opening {file}')

    def parse(self, file = None):
        '''
        Parse individual files, recursively evaluating includes/imports.
        '''
        self.stop = False
        file = file if file else self.src
        code = self.iterate(file)

        # Regular expressions for the main declarations
        r_define = re.compile(r'#(\w+):\s*"(.*)"')
        r_include = re.compile(r'include "(.*)"')
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
                    return self.quit(f'Improper syntax: {repr(line)}')
        except StopIteration:
            return self.quit(f'Incomplete script at:\n {repr(line)}')
        except Exception as e:
            return self.quit(f'Error at: {repr(line)}\nMessage: {e}')

    def parse_header(self, code, line, cat=None):
        '''
        Parse category or asset section header.
        '''
        r_asset = re.compile(r'(abstract)?\s*[Aa]sset (\w+)( extends (\w+))?')
        r_cat = re.compile(r'category (\w+)')
        r_meta = re.compile(r'([\w ]+):\s*"(.*)"')

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
            self.quit(f'Improper syntax: {repr(line)}')

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
                   Bernoulli(p)     Binomial(n, p)  Exponential(λ)           Gamma(k, θ)
                   LogNormal(μ, σ)  Pareto(x, α)    TruncatedNormal(μ, σ^2)  Uniform(a, b)
        {C,I,A}  (securiCAD only) confidentiality, integrity, availability (any combination)
        @hidden  (securiCAD only) hide from attack paths
        @debug   (securiCAD only) show only while testing
        @trace   (securiCAD only) trace intermediary steps, e.g. userAccount.assume -> action.perform
        '''
        r_attr = re.compile(r'([|&#E]{1}|[!E]{2})\s+(\w+)(\s+\[([\w(). ,]+)\])?')
        r_cia = re.compile(r'{\s*([CIA])(,\s*([CIA])(,\s*([CIA]))?)?\s*}')
        r_meta = re.compile(r'([\w ]+):\s*"(.*)"')
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
                field = last_attr[sym[pre]] = last_attr[sym[pre]] if sym[pre] in last_attr else {}
                line = line[2 + (not line[0].isalpha()):]
                self.parse_expression(code, line, field)
            else:
                self.quit(f'Improper syntax: {repr(line)}')

    def parse_expression(self, code, line, field):
        '''
        Parse asset expressions.
        '''
        r_let = re.compile(r'let ([A-Za-z_]\w*)\s*=\s*"?([^"]+)"?')
        m = [int(x) for x in field if x.isdigit()]
        i = max(m) + 1 if m else 0
        while 1:
            if (r := r_let.match(line)):
                name, value = r.groups()
            else:
                name, value, i = (i, line, i+1)
            field[str(name)] = value.rstrip(',')
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
        r_association = re.compile(r'(\w+)\s+\[(\w+)\]\s+([\d*.]+)\s+<--\s*(\w+)\s*-->\s+([\d*.]+)\s+\[(\w+)\]\s+(\w+)')
        r_meta = re.compile(r'([\w ]+):\s*"(.*)"')
        last_link = None

        while '}' not in (line := next(code)):
            if (r := r_association.match(line)):
                asset_l, field_l, mult_l, link, mult_r, field_r, asset_r = r.groups()
                if 'associations' not in self.result:
                    self.result['associations'] = []
                self.result['associations'].append({
                    'name': link,        'meta': {},
                    'asset_l': asset_l,  'asset_r': asset_r,
                    'field_l': field_l,  'field_r': field_r,
                    'mult_l' : mult_l,   'mult_r' : mult_r
                })
                last_link = self.result['associations'][-1]
            elif (r := r_meta.match(line)) and last_link:
                last_link['meta'][r.group(1)] = r.group(2)

def cli(arg):
    '''
    Handle command line arguments.
    '''
    usage = f'''
{w}Usage:{z} demal <{g}input{z}> [{c}output{z}] [-r|--reverse] [{y}debug{z}] [-v|--version]

{w}Read from stdin when {g}input {w}is {r}- {w}and write to stdout when {c}output {w}is {r}-

{w}By default{z} .mal {w}or{z} .json {w}is appended to the output filename, depending on the source, else{z} output.mal {w}or{z} output.json {w}is used.

Append {y}debug {w}to print parser trace messages.{z}
'''
    if '-v' in arg or '--version' in arg:
        print(__version__)
        sys.exit(0)
    if len(arg) < 2 or '-h' in arg or '--help' in arg:
        sys.exit(usage)
    elif arg[1] == '-':
        file = sys.stdin
    else:
        file = arg[1]
    out = None
    if len(arg) > 2:
        if arg[2] == '-':
            out = sys.stdout
        elif arg[2] in ('debug', '-r', '--reverse'):
            pass
        else:
            out = arg[2]
    return file, out, 'debug' in arg, any(x in arg[2:] for x in ('-r', '--reverse'))

def main():
    '''
    Run as a standalone application.
    '''
    file, out, debug, to_mal = cli(sys.argv)
    if file is not sys.stdin and not os.path.isfile(file):
        sys.exit(f'Error while opening {file}')
    if to_mal:
        with open(file) as f:
            mal = MalParser(file)
            mal.result = json.load(f)
            error = mal.dump_mal(out=out)
            if error:
                sys.exit(1)
        return
    mal = MalParser(file, debug=debug)
    error = mal.parse()
    if error:
        sys.exit(1)
    mal.dump(out=out, pretty=True)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nInterrupted.')
