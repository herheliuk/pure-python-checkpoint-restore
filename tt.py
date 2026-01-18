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

def ss():
    for i in range(1, 6):
        yield i

for i in ss():
    print(i)
