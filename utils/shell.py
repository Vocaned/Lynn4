import subprocess
import typing

def check_output(args: typing.List[str], timeout: int = 30):
    out = subprocess.check_output(args, stderr=subprocess.STDOUT, timeout=timeout)
    if isinstance(out, bytes):
        out = out.decode('utf-8')
    return out
