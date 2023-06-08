from dataclasses import dataclass


@dataclass
class Requirement:
    name: str
    extra: bool
    description: str
    raise_error: bool = False
    dummy: bool = True


def requires(*requirements: Requirement):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if all([x.extra for x in requirements]):
                return func(*args, **kwargs)
            else:
                print(f"Dependencies not met! {' -- '.join([r.description for r in requirements])}")
                print("Install optional dependencies with `poetry install --all-extras`")
                print("See README.md for more information.")
                if any([x.raise_error for x in requirements]):
                    raise ImportError(f"Essential packages not installed to call this function.")
                elif any([x.dummy for x in requirements]):
                    return lambda *args, **kwargs: None  # pyright: ignore
                else:
                    return func(*args, **kwargs)

        return wrapper

    return decorator
