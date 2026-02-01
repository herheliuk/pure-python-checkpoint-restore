try:
    print("OH, NOOOOO, MY SHAILA!!")
    0/0
except Exception as error:
    print("EXCEPTION:", error)
else:
    print("NO EXCEPTIONS, ALL GOOD!")
finally:
    print("finally")