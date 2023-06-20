from pathlib import Path


def getfilelist(mypath: str, suffix: str, withpath: bool = False) -> list[str] | list[Path]:
    """Find all files in folders and subfolders given a specific extension"""
    p = Path(mypath).glob("*." + suffix)
    l = [x for x in p if x.is_file()]
    l = [x for x in l if not x.name.startswith(".")]
    if withpath == False:
        l = [f.name for f in l]
    return l
