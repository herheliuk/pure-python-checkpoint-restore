### Usage:

python3 dump.py `<script_path>` `<dump_line>` `[dump_occurrence]` `[snapshot_path]` `{optimiation_level}`

python3 restore.py `<script_path>` `[snapshot_path]`

#### Example:

```
source env.sh

python -O dump.py test_files/miss.py 5 4
python -O restore.py test_files/miss.py
```

---

### Main idea:

``` python
def walk_frames_to_root(frame: FrameType) -> Iterator[FrameType]:
    while frame:
        yield frame
        frame = frame.f_back
```

Extract all useful data from these frames and rebuild the state in a new program.

---

### WIP:

- generators

#### known BUGS:

- generators doesn't work!
- dumpimg imp.py:95 - class triggers _enter_!?
- args for the file we're tracing

#### potential issues:

- async/await 🌚
- threads 🌚

&

- locals()['var'] = ... ; ast is blind to that ATM
- use frame_ids for all rewrites ; we may have a few instances!
- does main trace_function need paths_to_trace?

from 'for' block:

- generator expressions
- zip objects
- map/filter
- custom iterators

#### OPTIMISATIONS:

- use AST to determine which locals we need to dump &? -> SQL
