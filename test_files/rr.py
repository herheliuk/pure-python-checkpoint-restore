try:
    print("OH, NOOOOO, MY SHAILA!!")
    open("g", 'r')
except Exception as error:
    print("EXCEPTION:", error)
else:
    print("NO EXCEPTIONS, ALL GOOD!")
finally:
    print("finally")