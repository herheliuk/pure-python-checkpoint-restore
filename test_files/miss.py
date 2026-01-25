log = []
out = []

for i in range(1, 6):
    log.append(("top1", i))
    print(i)

for i in range(1, 6):
    log.append(("top2", i))

def hpfq():
    for i in range(1, 6):
        log.append(("hpfq1", i))
        yield i
    for i in range(1, 6):
        log.append(("hpfq2", i))
        yield i

def ss():
    for i in range(1, 6):
        log.append(("ss", i))
        def h2pfq():
            with open('s', 'w'):
                for i in range(1, 6):
                    log.append(("h2pfq", i))
                    yield from hpfq()
        yield from h2pfq()

for i in list(ss()):
    out.append(i)
    log.append(("out", i))

import dill

with open('miss', 'rb') as file:
    _out, _log = dill.load(file)

assert _out == out and _log == log, "MISMATCH"

print("GOOD")
