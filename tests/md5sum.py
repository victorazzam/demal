import io, sys, time, hashlib

def fs(files):
    for file in files:
        try:
            time.sleep(0.1)
            with io.open(file, 'rb') as f:
                md5 = hashlib.md5(f.read())
                print(md5.hexdigest())
        except IOError:
            sys.exit(f'Could not read {file}')

def cli():
    md5 = hashlib.md5()
    CRLF, LF = b'\r\n', b'\n'
    for line in sys.stdin.buffer:
        md5.update(line.replace(CRLF, LF))
    print(md5.hexdigest())

try:
    fs(sys.argv[1:]) if len(sys.argv) > 1 else cli()
except KeyboardInterrupt:
    sys.exit('\nInterrupted\n')