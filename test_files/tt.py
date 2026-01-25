try:
    pass
except:
    pass
finally:
    pass

if False:
    raise Exception("Never in my life...")
elif False:
    pass
else:
    pass

def hpfq():
    for i in range(1, 6): # 1..5
        yield i

def ss():
    for i in range(1, 6): # 1..5
        def h2pfq():
            with open('s', 'r'):
                for i in range(1, 6): # 1..5
                    hpfq()
        h2pfq()

for i in ss():
    print(i)
