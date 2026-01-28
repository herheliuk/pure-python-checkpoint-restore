def hpfq():
    for i in range(1, 6): # 1..5
        yield i

def ss():
    for i in range(1, 6): # 1..5
        
        def h2pfq():
            with open('s', 'w'):
                for i in range(1, 6): # 1..5
                    yield from hpfq()
        yield from h2pfq()

for i in ss():
    print(i)
