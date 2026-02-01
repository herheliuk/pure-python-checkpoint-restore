
https://youtu.be/B2ElZK0u85Y&t=60s

---

Usage: python3 dump.py `<file>` `<line number>` `<occurance>`

Usage: python3 restore.py `<file>`

example:
```
source env.sh

python3 dump.py test_files/miss.py 5 4
python3 restore.py test_files/miss.py
```

---

### Main idea:

``` python
def get_the_stack(frame: FrameType) -> Iterator[FrameType]:
    while frame:
        stack.append(frame)
        frame = frame.f_back
    
    yield from reversed(stack)
```

extract all useful data, save it and rebuild the state in a new program.

### planned Next steps:

- file descriptors
- async/await 🌚
- threads 🌚

'for' block, Cannot slice:

- generators
- generator expressions
- zip objects
- map/filter
- custom iterators

thease are not yet implemented/tested... ^

#### known BUGS:

- classes, (_enter_ call) ; they are not on the call stack...
- dumping for lines themselves ; opcodes run after the "line" event...
- ?use frames for rewrites and other mappings ; we can have a few instances of the same function!
- ?if for throws it will be on the stack twice

### planned OPTIMISATIONS:

- use AST to determine which locals we need to dump
- store only changes to locals (SQL table)
