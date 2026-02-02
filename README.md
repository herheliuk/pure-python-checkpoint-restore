
https://youtu.be/B2ElZK0u85Y&t=60s

---

### Usage:

python3 dump.py `<script_path>` `<dump_line>` `[dump_occurrence=1]` `[snapshot_path=snapshot]`

python3 restore.py `[snapshot_path=snapshot]` `[script_path=from(snapshot)]`

#### Example:

```
source env.sh

python dump.py test_files/miss.py 5 4
python restore.py
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

---

### WIP:

from 'for' block:

- generators
- generator expressions
- zip objects
- map/filter
- custom iterators

&

- async/await 🌚
- threads 🌚

#### known BUGS:

- locals()['var'] = ... ; ast is blind to that ATM
- miss.py:30 'for' forces call stack that should've been returned / never ran... ; for i in (hash_29 := list(ss())):
- imp.py:94 class triggers like _enter_ shouldn't be ran. ; get rid of _enter_ on all classes. but... what about C objects??
- file descriptors ; we're overwriting them with old locals / shouldn't have had ran as well... ; lsof ?
- use frames for all rewrites ; we may have a few instances of the same function!
- ? maybe tracing.py needs to return paths_to_trace; since returning self on calls

#### OPTIMISATIONS:

- use AST to determine which locals we need to dump &? -> SQL
