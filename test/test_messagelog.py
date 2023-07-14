from pathlib import Path
from tempfile import TemporaryDirectory

import storytime_ai.messagelog as messagelog


def test_messagelog():
    temp_dir = TemporaryDirectory()
    temp_file = Path(temp_dir.name) / "temp_file.html"
    messagelog.set_filename(temp_file)
    messagelog.log([{"heading": "unique heading", "content": "log content"}])
    messagelog.log([{"heading": "unique heading2 ", "content": "log content"}])
    with temp_file.open() as f:
        assert f.read().strip() != ""
        f.seek(0)
        assert "unique heading" in f.read()
    temp_dir.cleanup()


def test_messagelog_message():
    temp_dir = TemporaryDirectory()
    temp_file = Path(temp_dir.name) / "temp_file.html"
    messagelog.set_filename(temp_file)
    messagelog.messagelog([{"role": "Wurst", "content": "Testxt"}, {"role": "Wurst", "content": "Test2"}])
    messagelog.messagelog([{"role": "Wurst", "content": "Testxt"}])
    # import os
    # import time
    # os.system("xdg-open " + str(temp_file))
    # time.sleep(10)
    with temp_file.open() as f:
        assert f.read().strip() != ""
        f.seek(0)
        assert "Test2" in f.read()
    temp_dir.cleanup()


if __name__ == "__main__":
    test_messagelog()
