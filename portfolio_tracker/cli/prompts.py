import math

from portfolio_tracker.errors import InvalidInputError


def prompt_text(label: str) -> str:
    return input(label)


def prompt_int(label: str, field_name: str) -> int:
    raw = input(label).strip()
    try:
        return int(raw)
    except ValueError as err:
        raise InvalidInputError(
            f"Invalid {field_name} '{raw}'. Please enter a whole number."
        ) from err


def prompt_float(label: str, field_name: str) -> float:
    raw = input(label).strip()
    try:
        value = float(raw)
    except ValueError as err:
        raise InvalidInputError(
            f"Invalid {field_name} '{raw}'. Please enter a valid number."
        ) from err

    if math.isnan(value) or math.isinf(value):
        raise InvalidInputError(
            f"Invalid {field_name} '{raw}'. Please enter a valid number."
        )
    return value
