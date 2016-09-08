# ----------------------------------------------------------------------------------
#  Title      : Conversion tests
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : test_Conversions.py
#  Author     : Stefan Reichoer
#  Company    : MSC Technologies
#  Created    : 2016-09-07
# ----------------------------------------------------------------------------------
#  Description: Conversion tests
# ----------------------------------------------------------------------------------
#  Copyright (c) 2016 -- MSC Technologies
# ----------------------------------------------------------------------------------

import pytest

import MscBoost.Conversions as Conversions

def test_conversion_basics():
    with pytest.raises(Exception):
        assert Conversions.int_val("15.0", accept_float=False) == 15
    assert Conversions.int_val("15.0", accept_float=True) == 15
    assert Conversions.int_val("15.5", accept_float=True) == 15
    assert Conversions.int_val("15", accept_float=False) == 15
    assert Conversions.string_repr(42, "dummy") is None

def test_convert():
    assert Conversions.convert_value(1, "dummy") is None
    with pytest.raises(Exception):
        assert Conversions.convert_value(1, "dummy", raise_error=True)
    assert Conversions.convert_value("200", "storage-size") == 200

def test_convert_param():
    assert Conversions.convert_param_value("6 kB", "storage-size") == 6*1024
    with pytest.raises(Exception):
        assert Conversions.convert_param_value("6 kByte", "storage-size")

def test_value_with_unit():
    v = Conversions.create_value_with_unit("1kB", "storage-size")
    v2 = Conversions.create_value_with_unit("2kB", "storage-size")
    v_5B = Conversions.create_value_with_unit("5", "storage-size")
    assert repr(v) == "1kB"
    assert str(v) == "1kB"
    assert v.value == 1024
    assert float(v) == 1024.
    assert int(v) == 1024
    assert str(-v) == "-1kB"
    assert abs(-v).value == 1024
    assert v == v
    assert v2 > v
    assert str(v + 512) == "1.5kB"
    assert str(v + v2) == "3kB"
    assert str(v - 512) == "512B"
    assert str(v2 - v2) == "0B"
    assert str(v * 3) == "3kB"
    assert str(v * v2) == "2MB"  # multiplication does not consider units - only the value
    assert str(v / 2) == "512B"
    assert str(v2 / v) == "2B"  # division does not consider units - only the value
    assert str(v // 4) == "256B"
    assert str(v2 // v) == "2B"  # division does not consider units - only the value
    assert str(v % 3) == "1B"
    assert str(v2 % v) == "0B"
    assert str(v**2) == "1MB"
    assert str(v**v_5B) == "1024TB"
    assert str(512+v2) == "2.5kB"
    assert str(1024*8-v) == "7kB"
    assert str(8.6*v) == "8.6kB"
    assert str(2048/v) == "2B"
    assert str(2048//v2) == "1B"

def test_storage_size():
    assert Conversions.convert_value(1, "storage-size") == 1
    assert Conversions.convert_value("2", "storage-size") == 2
    assert Conversions.convert_value("8B", "storage-size") == 8
    assert Conversions.convert_value("1kB", "storage-size") == 1024
    assert Conversions.convert_value("1.5kB", "storage-size") == int(1024*1.5)
    assert Conversions.convert_value("1MB", "storage-size") == 1024*1024
    assert Conversions.convert_value("2GB", "storage-size") == 2*1024**3
    assert Conversions.convert_value("100TB", "storage-size") == 100*1024**4
    assert Conversions.convert_value("100byte", "storage-size") is None
    assert Conversions.string_repr(1, "storage-size") == "1B"
    assert Conversions.string_repr(1024*56, "storage-size") == "56kB"
    assert Conversions.string_repr(18*1024**2, "storage-size") == "18MB"
    assert Conversions.string_repr(6.7*1024**3, "storage-size") == "6.7GB"
    assert Conversions.string_repr(8.75*1024**4, "storage-size") == "8.75TB"
    assert Conversions.string_repr(1.126, "storage-size") == "1.13B"
