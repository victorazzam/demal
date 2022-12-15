import io, os, sys, json, demal, hashlib

def run(cmds):
    for cmd, md5, rem in cmds:
        print(f'Command: {cmd}')
        p = os.popen(cmd).read().strip()
        if rem:
            os.remove(rem)
        assert p == md5, f'Expected {md5} but found {repr(p)}'

def main():
    # Program to use to echo files
    view = 'type' if '\\' in os.popen('whoami').read() else 'cat'

    for file in ('test1.mal', 'test2.mal'):
        print(f'\nTesting: {file}')

        # To JSON
        m = demal.MalParser(file)
        m.parse()
        md5_1 = hashlib.md5(f'{m}\n'.encode()).hexdigest()
        cmds = [
          ( f'demal {file} | python md5sum.py {file}.json'            , md5_1 ,     None      ),
          ( f'demal {file} abc.json | python md5sum.py abc.json'      , md5_1 , 'abc.json'    ),
          ( f'demal {file} - | python md5sum.py'                      , md5_1 ,     None      ),
          ( f'{view} {file} | demal - | python md5sum.py output.json' , md5_1 , 'output.json' ),
          ( f'{view} {file} | demal - - | python md5sum.py'           , md5_1 ,     None      )
        ]
        run(cmds)

        # To MAL
        new = file + '.json'
        m = demal.MalParser(new)
        with io.open(new, newline='\n') as f:
            m.result = json.load(f)
        s = io.StringIO()
        m.dump_mal(out=s)
        s.seek(0)
        md5_2 = hashlib.md5(s.read().encode()).hexdigest()
        cmds += [
          ( f'demal {new} -r | python md5sum.py {new}.mal'             , md5_2 , new + '.mal' ),
          ( f'demal {new} abc.mal -r | python md5sum.py abc.mal'       , md5_2 , 'abc.mal'    ),
          ( f'demal {new} - -r | python md5sum.py'                     , md5_2 ,     None     ),
          ( f'{view} {new} | demal - -r | python md5sum.py output.mal' , md5_2 , 'output.mal' ),
          ( f'{view} {new} | demal - - -r | python md5sum.py'          , md5_2 , new          )
        ]
        run(cmds)

try:
    main()
    print('\nPassed\n')
except Exception as e:
    sys.exit(f'Error: {e}\n\nFailed\n')
