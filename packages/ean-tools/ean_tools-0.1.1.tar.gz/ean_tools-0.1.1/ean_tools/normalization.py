import re
from typing import Optional

from ean_tools.check_digits import get_correct_check_digit, has_correct_check_digit, isbn10_has_correct_check_digit


def normalize_barcode(barcode: str, is_isbn: Optional[bool] = None) -> str:
    """Normalizes a barcode.

    Args:
        barcode (str): The barcode string.
        is_isbn (Optional[bool]): Flag to indicate whether the barcode is an ISBN
        (to resolve possible ambiguity between ISBN-10 and EAN barcodes).

    Returns:
        str: The normalized barcode string.

    Raises:
        ValueError: If the barcode is invalid or ambiguous.
    """
    barcode = re.sub(r'[\s-]', '', barcode)
    if not barcode or not barcode.isdecimal() or barcode == '0' * len(barcode):
        raise ValueError("Doesn't look like a barcode")

    barcode_len = len(barcode)
    barcode_stripped = barcode.lstrip('0')
    barcode_stripped_len = len(barcode_stripped)

    if len(barcode) < 8:
        raise ValueError('Too short for a barcode')

    if barcode_stripped_len > 14:
        raise ValueError('Too long for a barcode')

    is_valid_isbn10 = barcode_len == 10 and isbn10_has_correct_check_digit(barcode)

    if is_isbn:
        if is_valid_isbn10:
            return convert_isbn10_to_isbn13(barcode)

        if barcode_len == 10 and not is_valid_isbn10:
            raise ValueError('Invalid ISBN')

        if barcode_len != 13 or not re.match(r'^97[8-9]', barcode):
            raise ValueError('Invalid ISBN')

    if barcode_len == 10 and is_isbn is None:
        is_valid_ean = has_correct_check_digit(barcode)

        if not is_valid_ean and is_valid_isbn10:
            return convert_isbn10_to_isbn13(barcode)

        if is_valid_ean is is_valid_isbn10:
            raise ValueError('Ambiguous ISBN-10 / EAN')

    if barcode_stripped_len in (13, 14, 8):
        return barcode_stripped

    return barcode_stripped.rjust(13, '0')


def convert_isbn10_to_isbn13(isbn10: str) -> str:
    """Converts an ISBN-10 barcode to ISBN-13 format.

    Args:
        isbn10 (str): The ISBN-10 barcode string.

    Returns:
        str: The corresponding ISBN-13 barcode string.
    """
    barcode = '978' + isbn10
    return barcode[:-1] + get_correct_check_digit(barcode)
