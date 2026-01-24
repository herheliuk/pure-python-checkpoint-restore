from sys import settrace, argv

args = list(map(int, argv[1:]))
pops = dict(zip(args[::2], args[1::2]))

def tracer(frame, event, arg):
    match event:
        case "line":
            line_no = frame.f_lineno
            if line_no in pops.keys():
                frame.f_lineno = pops[line_no]
        case "call":
            return tracer

settrace(tracer)

def main():
    print('>')
    if print('TOO LATE MAN'):
        ...
    elif print('TOO LATE MAN'):
        if False == True:
            print('No way...')
            if False == True:
                if False == True:
                    if False == True:
                        if False == True:
                            print('Never in my life...')
    print('<')

main()
