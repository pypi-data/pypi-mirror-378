import os
from typing import Optional

import yaml

from affix_tree import AffixTree

_CURRENT_DIR = os.path.dirname(__file__)


def init_gs1_prefixes() -> AffixTree[dict]:
    with open(os.path.join(_CURRENT_DIR, 'data/gs1-prefixes.yaml')) as gs1_prefixes_file:
        _gs1_prefixes = yaml.load(gs1_prefixes_file.read(), yaml.CBaseLoader)

    gs1_prefixes = AffixTree()
    for prefix_group in _gs1_prefixes:
        for p in prefix_group.pop('prefixes'):
            gs1_prefixes.add(p, prefix_group)

    return gs1_prefixes


def init_gs1_8_prefixes() -> AffixTree[dict]:
    with open(os.path.join(_CURRENT_DIR, 'data/gs1-8-prefixes.yaml')) as gs1_8_prefixes_file:
        _gs1_8_prefixes = yaml.load(gs1_8_prefixes_file.read(), yaml.CBaseLoader)

    gs1_8_prefixes = AffixTree()
    for prefix_group in _gs1_8_prefixes:
        for p in prefix_group.pop('prefixes'):
            gs1_8_prefixes.add(p, prefix_group)

    return gs1_8_prefixes


def init_isbn_prefixes() -> AffixTree[dict]:
    with open(os.path.join(_CURRENT_DIR, 'data/isbn-prefixes.yaml')) as isbn_prefixes_file:
        _isbn_prefixes = yaml.load(isbn_prefixes_file.read(), yaml.CBaseLoader)

    isbn_prefixes = AffixTree()
    for prefix_group in _isbn_prefixes:
        for p in prefix_group.pop('prefixes'):
            isbn_prefixes.add(p, prefix_group)

    return isbn_prefixes


_GS1_8_PREFIXES: AffixTree[dict] = init_gs1_8_prefixes()
_GS1_PREFIXES: AffixTree[dict] = init_gs1_prefixes()
_ISBN_PREFIXES: AffixTree[dict] = init_isbn_prefixes()


def get_raw_ean8_prefix_info(barcode: str) -> Optional[dict]:
    return _GS1_8_PREFIXES.find(barcode)


def get_raw_ean13_prefix_info(barcode: str) -> Optional[dict]:
    return _GS1_PREFIXES.find(barcode)


def get_raw_isbn_prefix_info(barcode: str) -> Optional[dict]:
    return _ISBN_PREFIXES.find(barcode)
