from pathlib import Path
from typing import Sequence


def getfilelist(mypath: str, suffix: str, withpath: bool = False) -> Sequence[str | Path]:
    """Find all files in folders and subfolders given a specific extension"""
    p = Path(mypath).glob("*." + suffix)
    file_list = [x for x in p if x.is_file()]
    file_list = [x for x in file_list if not x.name.startswith(".")]
    if not withpath:
        return [f.name for f in file_list]
    return file_list
