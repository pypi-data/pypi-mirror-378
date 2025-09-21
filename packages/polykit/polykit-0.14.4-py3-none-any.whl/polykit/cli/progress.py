"""Utilities for displaying progress messages and spinners."""

from __future__ import annotations

from contextlib import contextmanager
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar

from halo import Halo

from polykit.text import color as colorize
from polykit.text import print_color

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from pathlib import Path

    from polykit.text.types import TextColor

T = TypeVar("T")


def with_spinner(
    text: str = "Processing...",
    success: str | None = None,
    color: TextColor = "cyan",
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Display a spinner while the decorated function is running.

    Args:
        text: The text to display before the spinner. Defaults to "Processing...".
        success: The text to display when the function completes successfully. Defaults to "Done!".
        color: The color of the text. Defaults to 'cyan'.
    """

    def spinner_decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            spinner_text = colorize(text, color) if color else text
            spinner = Halo(text=spinner_text, spinner="dots", color=color)
            spinner.start()
            try:
                result = func(*args, **kwargs)
                if success:
                    spinner.succeed(colorize(success, color))
                else:
                    spinner.stop()
            except Exception as e:
                spinner.fail(colorize(f"Failed: {e}", "red"))
                raise
            finally:
                spinner.stop()
            return result

        return wrapper

    return spinner_decorator


@contextmanager
def halo_progress(
    item: str | Path | None = None,
    start_message: str = "Processing",
    end_message: str | None = "Processed",
    fail_message: str = "Failed",
    text_color: TextColor = "cyan",
    success_color: TextColor = "green",
    fail_color: TextColor = "red",
    show: bool = True,
) -> Generator[Halo | None, None, None]:
    """Context manager to display a Halo spinner while a block of code is executing, with customized
    start and end messages.

    Args:
        item: The name of the item being processed. Accepts string or Path.
        start_message: The start message to display.
        end_message: The end message to display. Can also be None, in which case the spinner is
                     cleared at the end with no message displayed. Good for cleaner output.
        fail_message: The fail message to display.
        text_color: The color of the spinner text. Defaults to 'cyan'.
        success_color: The color of the success message. Defaults to 'green'.
        fail_color: The color of the fail message. Defaults to 'red'.
        show: Whether to show the Halo spinner output. Defaults to True.

    Usage:
        file_path = "example.txt"
        with halo_progress(file_path) as spinner:
            process_file(file_path)

        You can use spinner.succeed() or spinner.fail() to update the spinner status.

    Yields:
        Halo: The Halo spinner.
    """
    if item:
        start_message = f"{start_message} {item}"
        if end_message is not None:
            end_message = f"{end_message} {item}"
        fail_message = f"{fail_message} {item}"

    if show:
        spinner = Halo(text=colorize(start_message, text_color), spinner="dots")
        spinner.start()
    else:
        spinner = None

    try:
        yield spinner
    except Exception as e:
        if spinner is not None and show:
            spinner.fail(colorize(f"{fail_message}: {e}", fail_color))
        else:
            print_color(f"{fail_message}: {e}", fail_color)
        raise
    if spinner and show:
        if end_message is not None:
            spinner.succeed(colorize(end_message, success_color))
        else:
            spinner.stop()
    elif show and end_message is not None:
        print_color(end_message, success_color)
