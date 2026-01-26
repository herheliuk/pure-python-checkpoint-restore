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