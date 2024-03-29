import asyncio
import typing
import lynn
from .formatting import codeblock

async def subprocess(*args, **kwargs):
    try:
        proc = await asyncio.create_subprocess_exec(*args, **kwargs)
        await proc.wait()
        return proc
    except asyncio.CancelledError:
        proc.terminate()
        raise

async def check_output(args: typing.List[str], timeout: int = 30, raise_on_error: bool = False):
    proc = await asyncio.wait_for(subprocess(args[0], *args[1:], stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT), timeout)
    out = await proc.stdout.read()
    out = out.decode('utf-8')

    if raise_on_error and proc.returncode != 0:
        lynn.Error(f'Shell process for `{args[0]}` exited with status `{proc.returncode}`', codeblock(out))
    return out
