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
    assert Conversions.float_val("15") == 15.0
    assert Conversions.float_val("15.3") == 15.3
    assert Conversions.string_repr(42, "dummy") is None

def test_convert():
    assert Conversions.convert_value(1, "dummy") is None
    with pytest.raises(Exception):
        assert Conversions.convert_value(1, "dummy", raise_error=True)
    assert Conversions.convert_value("200", "storage-size") is None
    assert Conversions.convert_value("200B", "storage-size") == 200

def test_convert_param():
    assert Conversions.convert_param_value("6 KiB", "storage-size") == 6*1024
    for interpretation in ("storage-size", "time"):
        with pytest.raises(Exception):
            assert Conversions.convert_param_value("++wrong-value++", interpretation)

def test_parameter_value():
    assert Conversions.parameter_value("size", "12KiB", "storage-size").value == 12*1024
    try:
        assert Conversions.parameter_value("size", "12k", "storage-size")
    except Exception as e:
        assert str(e) == "Parameter 'size': Couldn't convert '12k' as storage-size\nExamples: 2B. Possible units are B,KB,KiB,MB,MiB,GB,GiB,TB,TiB. KB has factor 1000, KiB factor 1024"
    assert Conversions.parameter_value("size", "8KiB", "storage-size", min="7KiB", max="8KiB").value == 8*1024
    try:
        assert Conversions.parameter_value("size", "8KiB", "storage-size", min="8.1KiB", max="9KiB")
    except Exception as e:
        assert str(e) == "Parameter 'size': value 8KiB is out of valid range: [8.1KiB..9KiB]"
    try:
        assert Conversions.parameter_value("size", "8KiB", "storage-size", min="8.1KiB")
    except Exception as e:
        assert str(e) == "Parameter 'size': value 8KiB is out of valid range: [8.1KiB..]"
    try:
        assert Conversions.parameter_value("size", "8KiB", "storage-size", max="7.9KiB")
    except Exception as e:
        assert str(e) == "Parameter 'size': value 8KiB is out of valid range: [..7.9KiB]"
    assert Conversions.parameter_value("size", "1KB", "storage-size").value == 1000
    assert Conversions.parameter_value("size", "1MB", "storage-size").value == 1000**2
    assert Conversions.parameter_value("size", "1GB", "storage-size").value == 1000**3
    assert Conversions.parameter_value("size", "1TB", "storage-size").value == 1000**4
    assert Conversions.parameter_value("size", "1KiB", "storage-size").value == 1024
    assert Conversions.parameter_value("size", "1MiB", "storage-size").value == 1024**2
    assert Conversions.parameter_value("size", "1GiB", "storage-size").value == 1024**3
    assert Conversions.parameter_value("size", "1TiB", "storage-size").value == 1024**4

def test_value_with_unit():
    v0 = Conversions.create_value_with_unit("0B", "storage-size")
    v = Conversions.create_value_with_unit("1KiB", "storage-size")
    v2 = Conversions.create_value_with_unit("2KiB", "storage-size")
    v_5B = Conversions.create_value_with_unit("5B", "storage-size")
    assert repr(v) == "1KiB"
    assert str(v) == "1KiB"
    assert v.value == 1024
    assert float(v) == 1024.
    assert int(v) == 1024
    assert bool(v0) is False
    assert bool(v) is True
    assert str(-v) == "-1KiB"
    assert abs(-v).value == 1024
    assert v == v
    assert v2 > v
    assert str(v + 512) == "1.5KiB"
    assert str(v + v2) == "3KiB"
    assert str(v - 512) == "512B"
    assert str(v2 - v2) == "0B"
    assert str(v * 3) == "3KiB"
    assert str(v * v2) == "2MiB"  # multiplication does not consider units - only the value
    assert str(v / 2) == "512B"
    assert str(v2 / v) == "2B"  # division does not consider units - only the value
    assert str(v // 4) == "256B"
    assert str(v2 // v) == "2B"  # division does not consider units - only the value
    assert str(v % 3) == "1B"
    assert str(v2 % v) == "0B"
    assert str(v**2) == "1MiB"
    assert str(v**v_5B) == "1024TiB"
    assert str(512+v2) == "2.5KiB"
    assert str(1024*8-v) == "7KiB"
    assert str(8.6*v) == "8.6KiB"
    assert str(2048/v) == "2B"
    assert str(2048//v2) == "1B"

def test_storage_size():
    assert Conversions.convert_value(1, "storage-size") == 1
    assert Conversions.convert_value("8B", "storage-size") == 8
    assert Conversions.convert_value("1KiB", "storage-size") == 1024
    assert Conversions.convert_value("1.5KiB", "storage-size") == int(1024*1.5)
    assert Conversions.convert_value("1MiB", "storage-size") == 1024*1024
    assert Conversions.convert_value("2GiB", "storage-size") == 2*1024**3
    assert Conversions.convert_value("100TiB", "storage-size") == 100*1024**4
    assert Conversions.convert_value("1KB", "storage-size") == 1000
    assert Conversions.convert_value("1MB", "storage-size") == 1000**2
    assert Conversions.convert_value("1GB", "storage-size") == 1000**3
    assert Conversions.convert_value("1TB", "storage-size") == 1000**4
    assert Conversions.convert_value("100byte", "storage-size") is None
    assert Conversions.string_repr(1, "storage-size") == "1B"
    assert Conversions.string_repr(1024*56, "storage-size") == "56KiB"
    assert Conversions.string_repr(18*1024**2, "storage-size") == "18MiB"
    assert Conversions.string_repr(6.7*1024**3, "storage-size") == "6.7GiB"
    assert Conversions.string_repr(8.75*1024**4, "storage-size") == "8.75TiB"
    assert Conversions.string_repr(1.126, "storage-size") == "1.13B"

def test_time():
    assert Conversions.convert_value(1, "time") == 1
    assert Conversions.convert_value(12.5, "time") == 12.5
    assert Conversions.convert_value("1ps", "time") == 1E-12
    assert Conversions.convert_value("8ns", "time") == 8E-9
    assert Conversions.convert_value("48.7us", "time") == 48.7E-6
    assert Conversions.convert_value("4ms", "time") == 0.004
    assert Conversions.convert_value("8s", "time") == 8
    assert Conversions.convert_value("30min", "time") == 30*60
    assert Conversions.convert_value("4h", "time") == 4*3600
    assert Conversions.convert_value("1:02:07.5", "time") == 1*3600+2*60+7.5
    assert Conversions.string_repr(4E-3, "time") == "4ms"
    assert Conversions.string_repr(8E-6, "time") == "8us"
    assert Conversions.string_repr(17E-9, "time") == "17ns"
    assert Conversions.string_repr(34.5E-12, "time") == "34.5ps"
    assert Conversions.string_repr(-5, "time") == "-5s"
    assert Conversions.string_repr(59, "time") == "59s"
    assert Conversions.string_repr(120, "time") == "2min"
    assert Conversions.string_repr(8*3600, "time") == "8h"
    assert Conversions.string_repr(59.5, "time") == "59.5s"
    assert Conversions.string_repr(62, "time") == "0:01:02"
    assert Conversions.string_repr(62.8, "time") == "0:01:02.8"
    assert Conversions.string_repr(121.5, "time") == "0:02:01.5"
    assert Conversions.string_repr(14*3600+4.33, "time") == "14:00:04.33"
