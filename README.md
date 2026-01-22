
Usage: python3 dump.py `<file>` `<line number>`

Usage: python3 restore.py `<file>`

example:
```
source env.sh

python3 dump.py file.py 43
python3 restore.py file.py
```

https://youtu.be/B2ElZK0u85Y&t=60s

---

### Next steps:
- rebuild the function stack: if, try, with, for, etc. (turn on opcodes in settrace, replace the values on runtime 😎?)
- dump and restore generators (i guess they are just undestructed frames, probably the same as restoring functions)
- restore file descriptors (probably just re-open files...)
- figure out dumping mid-transaction (roll a few lines back?)
- optionally rerun some lines that user wants?
- async/await 🌚 (I didn't go there yet)
- threads 🌚 (I didn't go there yet)

thease are not yet implemented/tested ^