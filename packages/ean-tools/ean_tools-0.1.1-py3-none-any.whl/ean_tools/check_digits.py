def has_correct_check_digit(normalized_barcode: str) -> bool:
    """Checks if the given barcode has the correct check digit.

    Args:
        normalized_barcode (str): Normalized barcode string.

    Returns:
        bool: True if the check digit is correct, False otherwise.
    """
    return get_correct_check_digit(normalized_barcode) == normalized_barcode[-1]


def get_correct_check_digit(normalized_barcode: str) -> str:
    """Calculates the correct check digit for a barcode.

    Args:
        normalized_barcode (str): Normalized barcode string.

    Returns:
        str: The correct check digit.
    """
    check_digit = 0
    barcode_length = len(normalized_barcode)

    i = barcode_length - 2
    while i >= 0:
        weight = 3 if (barcode_length - i) % 2 == 0 else 1
        check_digit += int(normalized_barcode[i]) * weight
        i -= 1

    return str((10 - (check_digit % 10)) % 10)


def isbn10_has_correct_check_digit(isbn10: str) -> bool:
    """Checks if an ISBN-10 barcode has the correct check digit.

    Args:
        isbn10 (str): The ISBN-10 barcode string.

    Returns:
        bool: True if the check digit is correct, False otherwise.
    """
    s = sum((10 - i) * int(c) for i, c in enumerate(isbn10))
    return s % 11 == 0
