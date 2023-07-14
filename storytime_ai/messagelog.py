import copy
from datetime import datetime
from importlib.resources import files
from pathlib import Path
from typing import Dict, List, Optional

from jinja2 import Environment, FileSystemLoader

entry_storage: List[Dict] = []
env = Environment(loader=FileSystemLoader("/"))
template_file = Path(str(files("storytime_ai.templates").joinpath("messagelog.html")))
template = env.get_template(str(template_file))
filename: Path = Path("log/output.html")


def add_to_log(log_items: Dict | List[Dict] = {}):
    if isinstance(log_items, Dict):
        add_one_to_log(log_items)
    elif isinstance(log_items, list):
        add_many_to_log(log_items)
    else:
        raise ValueError("messagelog takes only dictionaries")


def add_many_to_log(log_items: List[Dict] = []):
    for log_item in log_items:
        add_one_to_log(log_item)


def add_one_to_log(log_item: Dict = {}, heading: Optional[str] = None):
    assert isinstance(log_item, Dict), "log_item must be of type Dict"
    if heading is not None:
        log_item[heading] = heading
    if "heading" not in log_item:
        log_item["heading"] = "query " + str(len(entry_storage)) + " " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry_storage.append(copy.deepcopy(log_item))


def write_log():
    output = template.render(log_entries=entry_storage)
    with open(filename, "w") as f:
        f.write(output)


def set_filename(_filename: Path = Path("log/output.html")):
    global filename
    filename = _filename


def messagelog(msgs: List[Dict]):
    mymsg = copy.deepcopy(msgs)
    for x in mymsg:
        # replace every line that starts with "-" with a "<p>" and end the line with "</p>"
        con = x.get("content")
        if not con:
            continue
        con_lines = con.splitlines()
        new_con_lines = ["<p class='item'>" + line[1:] + "</p>" if line.startswith("-") else line for line in con_lines]
        new_con = "\n".join(new_con_lines)
        x["content"] = new_con
    add_to_log(dict(content=mymsg))
    write_log()


def log(log_item: Dict | List[Dict] = {}):
    add_to_log(log_item)
    write_log()


if __name__ == "__main__":
    Path("log/output.html").unlink(missing_ok=True)
    import random

    headings = []
    for _ in range(20):
        heading = "unique heading"
        heading += str(random.randint(1, 100))
        headings.append(
            {
                "heading": heading,
                "content": [dict(role="wurst", content="kjalkjds"), dict(role="wurst", content="kjalkjds")],
            }
        )
    log(headings)

    Path("output.html").unlink(missing_ok=True)
    headings = []
    for _ in range(20):
        headings.append(
            {
                "content": [dict(role="wurst", content="kjalkjds"), dict(role="wurst", content="kjalkjds")],
            }
        )
    log(headings)

    import os

    os.system("xdg-open log/output.html")
    #
    # with messagelog() as mlog:
    #     mlog([{"heading": "unique heading", "content": "log content"}])
    #     mlog([{"heading": "unique heading2 ", "content": "log content"}])
    #
    # with messagelog() as mlog:
    #
