from sys import settrace, argv

from warnings import filterwarnings; assert not filterwarnings("ignore", category=RuntimeWarning); del filterwarnings

# python o.py <on_this_line> <jump_to_this_line> <23> <25> ...

args = list(map(int, argv[1:]))
pops = dict(zip(args[::2], args[1::2]))

def tracer(frame, event, arg):
    line_no = frame.f_lineno
    if not (jump_to := pops.get(line_no)):
        print(event, line_no)
    match event:
        case "line":
            if jump_to:
                print(f'jump from {line_no} to {jump_to}')
                frame.f_lineno = jump_to
        case "call":
            return tracer

settrace(tracer)

def main():
    try:
        with open('o.py', 'r'):
            try:
                with open('o.py', 'r'):
                    for i in range(1,6):
                        print('NO')
                        raise ...
            except Exception as e:
                print(f'{e}')
    except:
        pass
    ...

main()
