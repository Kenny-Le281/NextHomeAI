"""Thin wrapper so runner.py can import get_region_ids despite the
hyphenated folder name 'Get-Region-Ids'."""

import importlib.util
from pathlib import Path

_module_path = Path(__file__).resolve().parent / "Get-Region-Ids" / "GetRegionID.py"
_spec = importlib.util.spec_from_file_location("GetRegionID", _module_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def get_region_ids_for_runner(city_name):
    return _mod.get_region_ids(city_name)
