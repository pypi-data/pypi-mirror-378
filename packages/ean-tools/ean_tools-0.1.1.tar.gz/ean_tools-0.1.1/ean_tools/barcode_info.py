from dataclasses import dataclass
from enum import Enum
from typing import Optional

from ean_tools.barcode_prefixes import get_raw_ean8_prefix_info, get_raw_ean13_prefix_info, get_raw_isbn_prefix_info


class BarcodeType(Enum):
    COUPON_ID = 'COUPON_ID'
    DEMO = 'DEMO'
    GENERAL_MANAGER_NUMBER = 'GENERAL_MANAGER_NUMBER'
    REFUND_RECEIPT = 'REFUND_RECEIPT'
    REGULAR = 'REGULAR'
    RESERVED_FOR_FUTURE = 'RESERVED_FOR_FUTURE'
    RESTRICTED_CIRCULATION = 'RESTRICTED_CIRCULATION'
    UNUSED = 'UNUSED'


@dataclass
class BarcodeInfo:
    barcode_type: BarcodeType
    description: str
    country: Optional[str]


def get_barcode_info(normalized_barcode: str) -> BarcodeInfo:
    """Retrieves information about a given barcode.

    Args:
        normalized_barcode (str): The normalized barcode string.

    Returns:
        BarcodeInfo: An object containing barcode information.
    """
    if len(normalized_barcode) == 13 and (normalized_barcode.startswith('978') or normalized_barcode.startswith('979')):
        barcode_info = get_raw_isbn_prefix_info(normalized_barcode)
        if not barcode_info:
            return BarcodeInfo(BarcodeType.REGULAR, 'ISBN', None)

        return BarcodeInfo(BarcodeType.REGULAR, barcode_info['description'], barcode_info.get('country'))

    if len(normalized_barcode) == 8:
        barcode_info = get_raw_ean8_prefix_info(normalized_barcode)
    elif len(normalized_barcode) == 14:
        barcode_info = get_raw_ean13_prefix_info(normalized_barcode[1:])
    else:
        barcode_info = get_raw_ean13_prefix_info(normalized_barcode)

    if not barcode_info:
        return BarcodeInfo(BarcodeType.RESERVED_FOR_FUTURE, 'Reserved for future use', None)

    if 'type' in barcode_info:
        barcode_type = BarcodeType[barcode_info['type']]
    else:
        barcode_type = BarcodeType.REGULAR

    return BarcodeInfo(barcode_type, barcode_info['description'], barcode_info.get('country'))
