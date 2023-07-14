import logging
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import colorlog


def get_log(name: str = "default", level=logging.DEBUG):
    """Get a custom logger.

    Parameters
    ----------
    name : str, optional
        Name of the logger, by default "default"
    level : int, optional
        Logging level, by default logging.DEBUG

    Returns
    -------
    logging.Logger
        A custom logger.

    Examples
    --------
    In the main script, use the following code to get a logger.
    ```
    import logging
    from mylog import get_log
    log = get_log("somename", level=logging.DEBUG)
    ```
    In other modules, use the following code to get a logger.
    The log entries will be passed on to the loger of the main script.
    ```
    import logging
    log = logging.getLogger("somename." + __name__)
    ```
    """
    filename = Path("log/" + datetime.now().strftime("%Y-%m-%d_%H-%M") + ".log")
    filename.parent.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger(name)
    log.setLevel(level)
    # formatter = colorlog.ColoredFormatter("%(log_color)s%(levelname)s: %(name)s: %(message)s")
    if len(log.handlers) == 0:
        sdlr = logging.StreamHandler()
        sdlr.setFormatter(colorlog.ColoredFormatter("%(log_color)s%(levelname)s: %(name)s: %(message)s"))
        log.addHandler(sdlr)
        hdlr = logging.FileHandler(filename)
        hdlr.setFormatter(logging.Formatter("%(levelname)s: %(name)s: %(message)s"))
        log.addHandler(hdlr)
    return log


@contextmanager
def filelog(log: logging.Logger, filename: str | Path):
    """Context manager to log to html code in a file.

    Args:
        log: logging.Logger
    """
    if isinstance(filename, str):
        filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(filename)
    fh.setLevel(logging.DEBUG)
    html_formatter = logging.Formatter(
        "<p>%(asctime)s - %(name)s - <span style='color:%(color)s'>%(levelname)s: %(message)s</span></p>"
    )
    fh.setFormatter(html_formatter)
    log.addHandler(fh)
    yield
    log.removeHandler(fh)
