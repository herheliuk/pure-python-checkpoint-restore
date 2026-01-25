from sys import settrace, argv

from warnings import filterwarnings; assert not filterwarnings("ignore", category=RuntimeWarning); del filterwarnings

# python o.py <on_this_line> <jump_to_this_line> <23> <25> ...

args = list(map(int, argv[1:]))
pops = dict(zip(args[::2], args[1::2]))

def tracer(frame, event, arg):
    line_no = frame.f_lineno
    #print(event, line_no)
    match event:
        case "line":
            if line_no in pops.keys():
                jump_to = pops[line_no]
                print("\033[F\033[K", end="")
                print(f'jump from {line_no} to {jump_to}')
                frame.f_lineno = jump_to
        case "call":
            return tracer

settrace(tracer)

def main():
    with open('tt.py', 'r') as file:
        lines = file.readlines()
        for line in lines[14:]:
            print(line, end='')
    ...

main()
