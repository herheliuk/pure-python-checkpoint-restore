def main():
    for i in range(1, 6):
        print(i)
            
    for i in range(1, 6):
        print(i)

    for i in ss():
        print(i)

def hpfq():
    for i in range(1, 6):
        yield i

def h2pfq():
    with open('s', 'w'):
        for i in range(1, 6):
            yield from hpfq()

def ss():
    for i in range(1, 6):
        yield from h2pfq()

main()