import io, os, sys, json, demal, hashlib

if 'win' in sys.platform:
    sys.exit('These tests are not compatible with Windows.')

try:
    for t in ('test1.mal', 'test2.mal'):

        # To JSON
        m = demal.MalParser(t)
        m.parse()
        md5 = hashlib.md5(f'{m}\n'.encode()).hexdigest()
        cmds = {
          f'demal {t} && md5sum {t}.json'            : None,
          f'demal {t} abc.json && md5sum abc.json'   : 'abc.json',
          f'demal {t} - | md5sum'                    : None,
          f'cat {t} | demal - && md5sum output.json' : 'output.json',
          f'cat {t} | demal - - | md5sum'            : None
        }
        print(f'Testing: {t}\nExpecting: {md5}\n')
        for cmd, rem in cmds.items():
            print(f'Command: {cmd}')
            p = os.popen(cmd).read()
            p = p.split()[0]
            if rem:
                os.remove(rem)
            print(f'Found: {p}\n')
            assert p == md5

        # To MAL
        del m
        name = f'{t}.json'
        m = demal.MalParser(name)
        with open(name) as f:
            m.result = json.load(f)
        s = io.StringIO()
        m.dump_mal(out=s)
        s.seek(0)
        md5 = hashlib.md5(s.read().encode()).hexdigest()
        cmds = {
          f'demal {name} -r && md5sum {name}.mal'         : f'{name}.mal',
          f'demal {name} abc.mal -r && md5sum abc.mal'    : 'abc.mal',
          f'demal {name} - -r | md5sum'                   : None,
          f'cat {name} | demal - -r && md5sum output.mal' : 'output.mal',
          f'cat {name} | demal - - -r | md5sum'           : name
        }
        print(f'Expecting: {md5}\n')
        for cmd, rem in cmds.items():
            print(f'Command: {cmd}')
            p = os.popen(cmd).read().split()[0]
            if rem:
                os.remove(rem)
            print(f'Found: {p}\n')
            assert p == md5

    print('Passed')
except AssertionError:
    sys.exit('Failed')
