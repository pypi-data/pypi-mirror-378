"""Helper functions and decorators for handling command line arguments in functions."""

from collections.abc import Callable
from functools import wraps
from inspect import BoundArguments, Signature
import sys
from typing import Annotated

from bear_dereth.introspection import get_function_signature

ArgsType = Annotated[list[str] | None, "ArgsType: A list of command line arguments or None to use sys.argv[1:]"]
"""A type alias for when command line arguments may be passed in or None to use sys.argv[1:]."""
CLIArgsType = Annotated[list[str], "CLIArgsType: A list of command line arguments specifically for CLI usage"]
"""A type alias for when command line arguments are expected to be passed in."""


def to_argv(args: ArgsType = None) -> list[str]:
    """A simple function to return command line arguments or a provided list of arguments.

    Args:
        args (list[str] | None): A list of arguments to return. If None, it will return sys.argv[1:].

    Returns:
        list[str]: The list of command line arguments.
    """
    return sys.argv[1:] if args is None else args


def args_parse[R](
    param_name: str = "args",
    handler: Callable[[], list[str]] = to_argv,
    process: Callable[[list[str]], R] | None = None,
) -> Callable[..., Callable[..., R]]:
    """A decorator factory to automatically inject command line arguments.

    Args:
        param_name (str): The name of the parameter to inject the arguments into. Default is
            "args".
        handler (Callable[..., ReturnType] | None): A custom handler function to retrieve the
            arguments. If None, it will use the default args_handler function.
        process_call (Callable[..., R2] | None): An optional function to process the
            arguments before passing them to the decorated function.

    Returns:
        Callable[..., Callable[..., T]]: A decorator that injects command line arguments into the
            specified parameter if it is not already provided.
    """

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> R:
            sig: Signature = get_function_signature(func)
            if param_name in sig.parameters and param_name not in kwargs:
                bound: BoundArguments = sig.bind_partial(*args, **kwargs)
                raw_args: list[str] = bound.arguments[param_name] if param_name in bound.arguments else handler()
                final_result: R | list[str] = process(raw_args) if process is not None else raw_args
                bound.arguments[param_name] = final_result
                return func(*bound.args, **bound.kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["ArgsType", "CLIArgsType", "args_parse"]

# if __name__ == "__main__":
#     from argparse import ArgumentParser, Namespace

#     def get_args(args: CLIArgsType) -> Namespace:
#         parser = ArgumentParser(description="Example CLI Argument Parser")
#         parser.add_argument("--name", type=str, help="Your name")
#         parser.add_argument("--age", type=int, help="Your age")
#         return parser.parse_args(args)

#     @args_parse(process=get_args)
#     def example(args: Namespace) -> Namespace:
#         arguments = args
#         print(type(arguments))
#         return arguments

#     print(example(["--name", "Alice", "--age", "30"]))
