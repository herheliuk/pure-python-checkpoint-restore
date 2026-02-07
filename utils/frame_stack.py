from types import FrameType
from typing import Iterator

def walk_frames_to_current(frame: FrameType) -> Iterator[FrameType]:
    """slower, more memory"""
    stack: list[FrameType] = []
    stack_append = stack.append
    
    while frame:
        stack_append(frame)
        frame = frame.f_back
    
    yield from reversed(stack)

def walk_frames_to_root(frame: FrameType) -> Iterator[FrameType]:
    while frame:
        yield frame
        frame = frame.f_back
