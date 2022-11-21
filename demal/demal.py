#!/usr/bin/env python3

'''
demal
-----
Description: MAL (Meta Attack Language) to JSON decoding library and command-line tool.
Repo: https://github.com/victorazzam/demal
Author: Victor Azzam
'''

__version__ = '1.2.2'

import io, re, sys, copy, json, inspect

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

    def iterate(self, file):
        '''
        Iterate a file line by line.
        '''
        w = '\x1b[97m' # white
        r = '\x1b[91m' # red
        z = '\x1b[m' # end
        try:
            file = file if file is sys.stdin else open(file)
            with file as f:
                data = f.read()

                # Remove comments.
                # https://codegolf.stackexchange.com/a/48346/79525 :D
                regex = r'("[^\n]*"(?!\\))|(//[^\n]*$|/(?!\\)\*[\s\S]*?\*(?!\\)/)'
                for comment in re.findall(regex, data, 8):
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
                    self.quit(f'Improper syntax: {repr(line)}')
        except StopIteration:
            self.quit(f'Incomplete script at:\n {repr(line)}')
        except Exception as e:
            self.quit(f'Error at: {repr(line)}\nMessage: {e}')

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
                self.quit(f'Improper syntax: {repr(line)}')

    def parse_expression(self, code, line, field):
        '''
        Parse asset expressions.
        '''
        r_let = re.compile(r'let ([A-Za-z_]\w*)\s*=\s*"?([^"]+)"?')
        i = 0
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

def cli(arg):
    '''
    Handle command line arguments.
    '''
    import os
    colors = 'win' not in sys.platform or any(os.getenv(x) is not None for x in ('WT_SESSION', 'WT_PROFILE_ID'))
    r, g, y, b, c, w, u, z = (f'\x1b[{x}m' * colors for x in (91,92,93,94,96,97,4,0))
    usage = f'''
{w}Usage:{z} demal <{g}input{z}> [{c}output{z}] [{y}debug{z}]\n
 {g}input {w}format:{z}  {u}somefile.mal{z}  {w}or {r}- {w}to read from stdin
 {c}output {w}format:{z} {u}somefile.json{z} {w}or {r}- {w}to write to stdout\n
 {w}if {c}output {w}is missing, the program will either:
  write to{z} {u}somefile.mal.json{z} {w}if {g}input {w}is{z} {u}somefile.mal{z}
  {w}write to{z} {u}output.mal.json{z} {w}if {g}input {w}is {r}- {w}(stdout)\n
 append {y}debug {w}to print debug trace messages{z}
'''
    if '-v' in arg or '--version' in arg:
        print(__version__)
        sys.exit(0)
    if len(arg) < 2:
        sys.exit(usage)
    elif arg[1] == '-':
        file = sys.stdin
    elif arg[1].lower().endswith('.mal'):
        file = arg[1]
    else:
        sys.exit(usage)
    out = None
    if len(arg) > 2:
        if arg[2] == '-':
            out = sys.stdout
        elif arg[2].lower().endswith('.json'):
            out = arg[2]
        elif arg[2] == 'debug':
            pass
        else:
            sys.exit(usage)
    return file, out, 'debug' in arg

def main():
    '''
    Run as a standalone application.
    '''
    file, out, debug = cli(sys.argv)
    mal = MalParser(file, debug=debug)
    mal.parse()
    mal.dump(out=out, pretty=True)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nInterrupted.')
