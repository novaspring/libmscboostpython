# ----------------------------------------------------------------------------------
#  Title      : Various conversions
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : Conversions.py
#  Author     : Stefan Reichoer
#  Company    : MSC Technologies
#  Created    : 2016-09-07
# ----------------------------------------------------------------------------------
#  Description: Various conversions
# ----------------------------------------------------------------------------------
#  Copyright (c) 2016 -- MSC Technologies
# ----------------------------------------------------------------------------------

import time

from MscBoost.UsageException import UsageException

def int_val(value, unit="", multiplicator=1, accept_float=True):
    if unit:
        s_val = value[:-len(unit)]
    else:
        s_val = value
    if accept_float:
        num_val = float(s_val)
    else:
        num_val = int(s_val)
    num_val *= multiplicator
    return int(num_val)

def float_val(value, unit="", multiplicator=1):
    if unit:
        s_val = value[:-len(unit)]
    else:
        s_val = value
    num_val = float(s_val)
    num_val *= multiplicator
    return num_val

class ConversionBase(object):
    name = None
    def examples(self):
        return ""  # pragma: no cover

class ConvertStorageSize(ConversionBase):
    name = "storage-size"
    def examples(self):
        return "2B. Possible units are B,KB,KiB,MB,MiB,GB,GiB,TB,TiB. KB has factor 1000, KiB factor 1024"
    def convert(self, value):
        retval = None
        # Units should match C++ libMscBoost
        if type(value) == str:
            if value.endswith("TiB"):
                retval = int_val(value, "TiB", 1024**4)
            elif value.endswith("TB"):
                retval = int_val(value, "TB", 1000**4)
            elif value.endswith("GiB"):
                retval = int_val(value, "GiB", 1024**3)
            elif value.endswith("GB"):
                retval = int_val(value, "GB", 1000**3)
            elif value.endswith("MiB"):
                retval = int_val(value, "MiB", 1024**2)
            elif value.endswith("MB"):
                retval = int_val(value, "MB", 1000**2)
            elif value.endswith("KiB"):
                retval = int_val(value, "KiB", 1024)
            elif value.endswith("KB"):
                retval = int_val(value, "kB", 1000)
            elif value.endswith("B"):
                retval = int_val(value, "B")
        else:
            retval = value
        return retval
    def string_repr(self, value):
        if value < 0:
            sign_str = "-"
            value = abs(value)
        else:
            sign_str = ""
        for level, unit in [(1024**4, "TiB"), (1000**4, "TB"), (1024**3, "GiB"), (1000**3, "GB"), (1024**2, "MiB"), (1000**2, "MB"), (1024**1, "KiB"), (1000**1, "KB"), (None, "B")]:
            if level:
                if value >= level:
                    val = value / level
                    break
            else:
                val = value
        str_val = "%1.2f" % val
        str_val = str_val.rstrip("0")  # e.g. 100.00 -> 100.
        str_val = str_val.rstrip(".")  # e.g. 100. -> 100
        return "%s%s%s" % (sign_str, str_val, unit)

class ConvertTime(ConversionBase):
    name = "time"
    def examples(self):
        return "1ps, 2.3ns, 8us, 8.5ms, 1s, 6min, 2hr, 2:15:59.25"
    def convert(self, value):
        retval = None
        if type(value) == str:
            if value.endswith("ps"):
                retval = float_val(value, "ps", 1E-12)
            elif value.endswith("ns"):
                retval = float_val(value, "ns", 1E-9)
            elif value.endswith("us"):
                retval = float_val(value, "us", 1E-6)
            elif value.endswith("ms"):
                retval = float_val(value, "ms", 1E-3)
            elif value.endswith("s"):
                retval = float_val(value, "s")
            elif value.endswith("min"):
                retval = float_val(value, "min", 60)
            elif value.endswith("h"):
                retval = float_val(value, "h", 3600)
            elif value.count(":") == 2:
                hr, min, sec = value.split(":")
                retval = int(hr)*3600 + int(min)*60 + float(sec)
        else:
            retval = value
        return retval
    def string_repr(self, value):
        if value < 0:
            sign_str = "-"
            value = abs(value)
        else:
            sign_str = ""
        if value < 1.0:
            for level, unit in [(1E-3, "ms"), (1E-6, "us"), (1E-9, "ns"), (None, "ps")]:
                if level:
                    if value >= level:
                        val = value / level
                        break
                else:
                    val = value / 1E-12
        else:
            int_value = int(value)
            if int_value % 3600 == 0:
                val = int_value / 3600
                unit = "h"
            elif int_value % 60 == 0:
                val = int_value / 60
                unit = "min"
            else:
                if int_value < 60:
                    val = value
                    unit = "s"
                # if int_value > 60 and abs(value-int_value) > 1E-15:
                else:
                    midnight = time.mktime((0, 1, 2, 0, 0, 0, 0, 1, 0))
                    msecs = ("%.2f" % (value-int_value))[1:]
                    time_str = "%s%s" % (time.strftime("%H:%M:%S", time.localtime(midnight + int_value)), msecs)
                    time_str = time_str.rstrip("0")
                    time_str = time_str.rstrip(".")
                    if time_str.startswith("0"):
                        time_str = time_str[1:]
                    return time_str
        str_val = "%1.2f" % val
        str_val = str_val.rstrip("0")  # e.g. 100.00 -> 100.
        str_val = str_val.rstrip(".")  # e.g. 100. -> 100
        return "%s%s%s" % (sign_str, str_val, unit)

CONVERSION_MAPPING = {}
for obj in list(globals().values()):
    if isinstance(obj, type) and issubclass(obj, ConversionBase):
        if obj.name:
            CONVERSION_MAPPING[obj.name] = obj()

def convert_value(value, interpretation, raise_error=False, create_value_object=False, parameter_name=None):
    if interpretation in CONVERSION_MAPPING:
        conv = CONVERSION_MAPPING[interpretation]
        try:
            result = conv.convert(value)
        except:
            result = None
        if result is None:
            extra_info = "Examples: %s" % conv.examples()
    else:
        result = None
        extra_info = "Possible interpretations: %s" % ", ".join(CONVERSION_MAPPING.keys())
    if result is None and raise_error:
        exception_msg = "Couldn't convert '%s' as %s\n%s" % (value, interpretation, extra_info)
        if parameter_name is not None:
            exception_msg = "Parameter '%s': %s" % (parameter_name, exception_msg)
        raise Exception(exception_msg)
    if create_value_object and result is not None:
        result = ValueWithUnit(result, conv)
    return result

def convert_param_value(value, interpretation):
    try:
        result = convert_value(value, interpretation, raise_error=True)
    except Exception as e:
        raise UsageException(str(e))
    return result

def string_repr(value, interpretation):
    if interpretation in CONVERSION_MAPPING:
        conv = CONVERSION_MAPPING[interpretation]
        return conv.string_repr(value)
    else:
        return None

class ValueWithUnit(object):
    """
    Handle floating point numbers including a unit.
    """
    def __init__(self, value, converter):
        self.value = value
        self.converter = converter
    def __repr__(self):
        return self.converter.string_repr(self.value)

    def __float__(self):
        return float(self.value)
    def __int__(self):
        return int(self.value)
    def __bool__(self):
        return bool(self.value)
    def _build_retval(self, value):
        return self.__class__(value, self.converter)
    def __neg__(self):  # -a
        return self._build_retval(-self.value)
    def __abs__(self):  # abs(a)
        return self._build_retval(abs(self.value))
    def __lt__(self, other):  # a < b
        return self.value < other.value
    def __add__(self, other):  # a + b
        if isinstance(other, ValueWithUnit):
            return self._build_retval(self.value + other.value)
        else:
            return self._build_retval(self.value + other)
    def __sub__(self, other):  # a - b
        if isinstance(other, ValueWithUnit):
            return self._build_retval(self.value - other.value)
        else:
            return self._build_retval(self.value - other)
    def __mul__(self, other):  # a * b
        if isinstance(other, ValueWithUnit):
            return self._build_retval(self.value * other.value)
        else:
            return self._build_retval(self.value * other)
    def __truediv__(self, other):  # a / b
        if isinstance(other, ValueWithUnit):
            return self._build_retval(self.value / other.value)
        else:
            return self._build_retval(self.value / other)
    def __floordiv__(self, other):  # a // b
        if isinstance(other, ValueWithUnit):
            return self._build_retval(self.value // other.value)
        else:
            return self._build_retval(self.value // other)
    def __mod__(self, other):  # a % b
        if isinstance(other, ValueWithUnit):
            return self._build_retval(self.value % other.value)
        else:
            return self._build_retval(self.value % other)
    def __pow__(self, other):  # a ** b
        if isinstance(other, ValueWithUnit):
            return self._build_retval(self.value ** other.value)
        else:
            return self._build_retval(self.value ** other)
    def __radd__(self, other):  # other + self
        return self._build_retval(other + self.value)
    def __rsub__(self, other):  # other - self
        return self._build_retval(other - self.value)
    def __rmul__(self, other):  # other * self
        return self._build_retval(other * self.value)
    def __rtruediv__(self, other):  # other / self
        return self._build_retval(other / self.value)
    def __rfloordiv__(self, other):  # other // self
        return self._build_retval(other // self.value)

def create_value_with_unit(value, interpretation, raise_error=True):
    return convert_value(value, interpretation, raise_error=raise_error, create_value_object=True)

def parameter_value(parameter_name, value, interpretation, min=None, max=None):
    value = convert_value(value, interpretation, raise_error=True, create_value_object=True, parameter_name=parameter_name)
    value_error = False
    min_bound = ""
    max_bound = ""
    if min is not None:
        min_bound = convert_value(min, interpretation, create_value_object=True)
        if value < min_bound:
            value_error = True
    if max is not None:
        max_bound = convert_value(max, interpretation, create_value_object=True)
        if value > max_bound:
            value_error = True
    if value_error:
        exception_msg = "Parameter '%s': value %s is out of valid range: [%s..%s]" % (parameter_name, value, min_bound, max_bound)
        raise Exception(exception_msg)
    return value
