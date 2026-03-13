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
        
for i in ss():
    out.append(i)
    log.append(("out", i))


if __name__ == "__main__":
    import dill

    if __debug__:
        with open(script_dir / 'miss', 'rb') as file:
            _out, _log = dill.load(file)
            
        _bad_values = 0

        for x, y in zip(_log, log):
            if x != y:
                _bad_values += 1
        
        logs_len = len(_log) + len(log)
        
        print(f'🧃 {logs_len - _bad_values} | 🔥 {_bad_values}')
        
        bad_values = 0
        
        for i in _log:
            if i in log:
                log.remove(i)
            else:
                bad_values += 1

        for i in log:
            if i in _log:
                _log.remove(i)
            else:
                bad_values += 1
        
        logs_len = len(_log) + len(log)
        
        print(f'🧃 {logs_len - bad_values} | 🔥 {bad_values}')

        if not _bad_values and not bad_values:
            print("\033[32m" + "HAROSHAYA RABOTA OLEG!")
    else:
        with open(script_dir / 'miss', 'wb') as file:
            dill.dump((out, log), file)
        
        print('\033[32m' + 'Saved.')