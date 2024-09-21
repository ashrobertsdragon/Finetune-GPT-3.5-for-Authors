import sys

from loguru import logger


def stout_logger() -> None:
    """
    Set up loguru logger with stdout
    """
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time}</green> <level>{message}</level>",
    )


def format_args(args: list | None) -> str:
    "Create comma delimited string of arguments passed to logger"
    return ", ".join(args) if args else ""


def format_kwargs(kwargs: dict) -> str:
    "Create a comma delimited string of keyword arguments passed to logger"
    kwarg_list = [
        f"{key}={'text' if key == 'file_content' else value}"
        for key, value in kwargs.items()
        if key != "exception"
    ]
    return ", ".join(kwarg_list)


def construct_message(
    action: str,
    arg_str: str,
    kwarg_str: str,
    is_error: bool,
    exception: Exception | None = None,
) -> str:
    """
    Formats the log message body

    Args:
        action (str): The action performed.
        arg_str (str): The logger's *args parsed into a string.
        kwarg_str (str): The logger's **kwargs parsed into a string.
        is_error (bool): Whether or not the log message is for an Exception.
        exception (Exception | None): The exception being logged if there is
            one, defaults to None.

    Returns:
        str: The log message body formatted as a string.
    """
    messages = [
        f"Error performing {action} with"
        if is_error
        else f"{action} returned",
        f" {arg_str}{kwarg_str}",
    ]
    if exception:
        messages.append(f"\nException: {exception}")
    return "".join(messages)


def supabase_logger(
    level: str, action: str, is_error: bool = False, *args, **kwargs
) -> None:
    """
    Log actions from Supabase

    Args:
        level (str): The log level.
        action (str): The action being logged.
        is_level (bool): Whether the action resulted in an exception. Defaults
            to False.
        *args (Any): Any additional arguments passed to the logger.
        **kwargs (Any): Any additional keywords arguments passed to the logger.
    """
    arg_str = format_args(args)
    kwarg_str = format_kwargs(kwargs)
    exception = kwargs.get("exception", None)

    log_message = construct_message(
        action, arg_str, kwarg_str, is_error, exception
    )
    getattr(logger, level)(log_message)
