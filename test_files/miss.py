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

from pathlib import Path

script_dir = Path(__file__).parent

def ss():
    for i in range(1, 6):
        log.append(("ss", i))
        def h2pfq():
            with open(script_dir / 's', 'w'):
                for i in range(1, 6):
                    log.append(("h2pfq", i))
                    yield from hpfq()
        yield from h2pfq()

class _ss:
    def __iter__(self):
        yield from ss()

for i in _ss():
    out.append(i)
    log.append(("out", i))


if __name__ == "__main__":
    import dill

    if __debug__:
        with open(script_dir / 'miss', 'rb') as file:
            _out, _log = dill.load(file)
            
        bad_values = 0

        for x, y in zip(_log, log):
            if x != y:
                bad_values += 1

        assert not bad_values, print(f'{bad_values}/{len(_log) + len(log)}')
        if _log == log and _out == out:
            print("\033[32m" + "HAROSHAYA RABOTA OLEG!")
    else:
        with open(script_dir / 'miss', 'wb') as file:
            dill.dump((out, log), file)
        
        print('\033[32m' + 'Saved.')