import logging


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
    log = logging.getLogger(name)
    log.setLevel(level)
    hdlr = logging.StreamHandler()
    log.addHandler(hdlr)
    return log
