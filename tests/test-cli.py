import os, demal, hashlib

try:
    for t in ('test1.mal', 'test2.mal'):
        m = demal.MalParser(t)
        m.parse()
        md5 = hashlib.md5(repr(m).encode()).hexdigest()
        cmds = {
            f'python demal.py {t} && md5sum {t}.json': f'{t}.json',
            f'python demal.py {t} abc.json && md5sum abc.json': 'abc.json',
            f'python demal.py {t} - | md5sum': None,
            f'cat {t} | python demal.py - && md5sum output.mal.json': 'output.mal.json',
            f'cat {t} | python demal.py - - | md5sum': None
        }
        print(f'Testing: {t}\nExpecting: {md5}\n')
        for cmd in cmds:
            p = os.popen(cmd).read().split()[0]
            if cmds[cmd]:
                os.remove(cmds[cmd])
            print(f'Command: {cmd}\nFound: {p}\n')
            assert p == md5
    print('Passed')
except AssertionError:
    print('Failed')
