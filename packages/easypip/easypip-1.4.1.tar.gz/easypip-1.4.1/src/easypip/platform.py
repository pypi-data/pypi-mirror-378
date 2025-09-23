from functools import lru_cache
import logging
import re
import subprocess
from packaging.version import parse as parse_version, Version


@lru_cache()
def cuda_version() -> Version:
    """Returns the CUDA version"""
    try:
        re_cuda = re.compile(rb".*CUDA version: ([\d\.]+)", re.IGNORECASE)
        out = subprocess.check_output("nvidia-smi")
        for line in out.splitlines():
            m = re_cuda.match(line)
            if m:
                return parse_version(m.group(1).decode("utf-8"))
    except Exception:
        pass
    logging.info("No CUDA detected")
