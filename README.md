
https://youtu.be/B2ElZK0u85Y&t=60s

---

CURRENTLY BROKEN ⚠️, try `74141d6` or `f72baa4`

---

### Main idea:

``` python
frame = sys._getframe()
# or sys.settrace(trace_func)
# trace_func(frame, event, arg)
```

``` python
from types import FrameType
from typing import Iterator

def get_frame_stack(frame: FrameType) -> Iterator[FrameType]:
    """Yield frames from the root frame to the given frame."""
    stack: list[FrameType] = []
    stack_append = stack.append
    
    while frame:
        stack_append(frame)
        frame = frame.f_back
    
    yield from reversed(stack)
```

extract all useful data, save it and rebuild the state in a new program.

### Work in progress

<img src="images/work in progress.png" alt="Use ast to find and modify the code blocks in a way that rebuilds the stack, then inject the old scope on restore"/>

<img src="images/potential fixes.png" alt="increment line counter on each line and create a map of offsets with ast to navigate code block storage"/>

Curently working on: identifying code block boundaries, saving and applying ast rewrites, finding out current iteration for dumps

- rebuild the block stack (almost there, but we need to pop the trash from it)
- current iteration
- generators
- classes (_enter_) 🌚
- restore file descriptors
- async/await 🌚
- threads 🌚

<img src="images/ast modifications.png" alt="we can slice for's with ast before compilation, but we cannot slice: generators, zip objects, map/filter, other iterators"/>

yep. thease are not yet implemented/tested... ^

### FUTURE OPTIMISATIONS:

- use AST to determine which locals we need to dump
- store only changes to locals (SQL table)

<img src="images/call stack.png" alt="call stack: list[tuple[int, dict]]"/>

### Draft of a Restore process:

``` python
with open('snapshot', 'rb') as data:
    call_stack = dill.load(data)

# read the source code

# apply the ast patch

# compile and exec under settrace(trace_function)

def trace_function(frame, event, arg):
    if call_stack:
        match event:
            case 'line':
                frame.f_lineno, f_locals = call_stack.pop()
                for key, value in f_locals.items():
                    frame.f_locals[key] = value
            case 'call':
                return trace_function
```

---

Usage: python3 dump.py `<file>` `<line number>` `<occurance>`

Usage: python3 restore.py `<file>`

example:
```
source env.sh

python3 dump.py test_files/file.py 43
python3 restore.py test_files/file.py
```
