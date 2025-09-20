# ean-tools

Collection of tools for validating and getting information about EAN (UPC, GTIN) and ISBN barcodes.

## Installation

```commandline
pip install ean-tools
```

## Usage

### Barcode normalization

```pycon
>>> from ean_tools.normalization import normalize_barcode

>>> normalize_barcode('978-84865-4608-3')

'9788486546083'
```

### Check digit validation

```pycon
>>> from ean_tools.check_digits import has_correct_check_digit

>>> has_correct_check_digit('8510000076279')

False
```

### Getting additional barcode information

```pycon
>>> from ean_tools.barcode_info import get_barcode_info, BarcodeType

>>> get_barcode_info('4000000001140')

BarcodeInfo(barcode_type=BarcodeType.REGULAR, description='GS1 Germany', country='de')
```
