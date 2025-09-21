"""
Performance and stress test traceback fixtures.
"""


def generate_large_traceback(num_frames: int = 100) -> str:
    """
    Generate a large traceback with many frames for performance testing.

    Parameters
    ----------
    num_frames : int
        Number of stack frames to generate

    Returns
    -------
    str
        Large traceback string
    """
    frames = []
    for i in range(num_frames):
        frames.append(f'  File "module_{i}.py", line {i + 1}, in function_{i}')
        frames.append(f"    call_function_{i + 1}()")

    return (
        "Traceback (most recent call last):\n"
        + "\n".join(frames)
        + "\nRuntimeError: Large traceback test"
    )
