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

class ConversionBase(object):
    name = None
    def examples(self):
        return ""  # pragma: no cover

class ConvertStorageSize(ConversionBase):
    name = "storage-size"
    def examples(self):
        return "1, 2B, 1.5kB, 2MB, 4GB, 1TB"
    def convert(self, value):
        retval = None
        if type(value) == str:
            if value.endswith("TB"):
                retval = int_val(value, "TB", 1024**4)
            elif value.endswith("GB"):
                retval = int_val(value, "GB", 1024**3)
            elif value.endswith("MB"):
                retval = int_val(value, "MB", 1024**2)
            elif value.endswith("kB"):
                retval = int_val(value, "kB", 1024)
            elif value.endswith("B"):
                retval = int_val(value, "B")
            else:
                retval = int_val(value)
        else:
            retval = value
        return retval
    def string_repr(self, value):
        if value < 0:
            sign_str = "-"
            value = abs(value)
        else:
            sign_str = ""
        for level, unit in [(1024**4, "TB"), (1024**3, "GB"), (1024**2, "MB"), (1024**1, "kB"), (None, "B")]:
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

CONVERSION_MAPPING = {}
for obj in list(globals().values()):
    if isinstance(obj, type) and issubclass(obj, ConversionBase):
        if obj.name:
            CONVERSION_MAPPING[obj.name] = obj()

def convert_value(value, interpretation, raise_error=False, create_value_object=False):
    if interpretation in CONVERSION_MAPPING:
        conv = CONVERSION_MAPPING[interpretation]
        try:
            result = conv.convert(value)
        except:
            result = None
            extra_info = "Examples: %s" % conv.examples()
    else:
        result = None
        extra_info = "Possible interpretations: %s" % ", ".join(CONVERSION_MAPPING.keys())
    if result is None and raise_error:
        raise Exception("Couldn't convert '%s' as %s\n%s" % (value, interpretation, extra_info))
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
