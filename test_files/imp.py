#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import functools
import itertools
import statistics
from dataclasses import dataclass, field
# from enum import Enum # BUG
from pathlib import Path
from typing import Iterable, Generator

# ---------- enums ----------
from modes import Mode

# ---------- decorator ----------
def once(fn):
    called = False
    @functools.wraps(fn)
    def wrapper(*a, **k):
        nonlocal called
        if not called:
            called = True
            return fn(*a, **k)
    return wrapper

@once
def banner():
    print("📊 Text Analyzer")

# ---------- context manager ----------
class timer:
    def __enter__(self):
        import time
        self.start = time.perf_counter()
        return self
    def __exit__(self, *_):
        import time
        print(f"⏱ {time.perf_counter() - self.start:.4f}s")

# ---------- dataclass ----------
@dataclass(slots=True)
class Stats:
    count: int
    avg_len: float
    top: list[str] = field(default_factory=list)

# ---------- generators ----------
def words(lines: Iterable[str]) -> Generator[str, None, None]:
    for line in lines:
        yield from line.split()

# ---------- async ----------
async def read(path: Path) -> list[str]:
    return path.read_text().splitlines()

# ---------- core logic ----------
def analyze(lines: list[str], mode: Mode) -> Stats:
    match mode:
        case Mode.LINES:
            items = lines
        case Mode.WORDS:
            items = list(words(lines))

    lengths = [len(x) for x in items if (n := len(x)) > 0]  # walrus
    top = [
        k for k, _ in itertools.islice(
            sorted(
                ((x, items.count(x)) for x in set(items)),
                key=lambda t: t[1],
                reverse=True,
            ),
            5,
        )
    ]

    return Stats(
        count=len(items),
        avg_len=statistics.mean(lengths) if lengths else 0,
        top=top,
    )

# ---------- CLI ----------
def main():
    p = argparse.ArgumentParser()
    p.add_argument("file", type=Path)
    p.add_argument("dump_no", type=int)
    p.add_argument("--mode", choices=[m.value for m in Mode], default="words")
    args = p.parse_args()

    banner()

    with timer():
        lines = asyncio.run(read(args.file))
        stats = analyze(lines, Mode(args.mode))

    print(f"""
Count   : {stats.count}
Average : {stats.avg_len:.2f}
Top     : {", ".join(stats.top)}
""")

if __name__ == "__main__":
    main()
