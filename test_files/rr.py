try:
    print("OH, NOOOOO, MY SHAILA!!")
    raise Exception("SKIP")
    ...
except Exception as error:
    print("EXCEPTION:", error)
