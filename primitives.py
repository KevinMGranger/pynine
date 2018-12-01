import attr
import construct
import enum
import typing
from functools import partial


CONSTRUCT = '__construct'


def attribute(constructor, type_, validator=None, metadata=None, **kwargs):
    """
    Create an attr.ib with the given construct in the metadata.
    """
    metadata = {} if not metadata else metadata
    metadata[CONSTRUCT] = constructor
    return attr.ib(type=type_, validator=validator, metadata=metadata, **kwargs)


def _validator_maybe(new_validator, validator):
    if isinstance(validator, list):
        validator.append(new_validator)
    elif validator is None:
        validator = new_validator
    else:
        validator = [validator, new_validator]

    return validator


def unsigned(bits: int, validator=None, **kwargs):
    max_value = 2**bits - 1

    def value_in_range(_, __, value: int):
        if not 0 <= value <= max_value:
            raise ValueError(f"value must be between 0 and {max_value}")
    
    return attribute(getattr(construct, f"Int{bits}ul"), int,
        validator=_validator_maybe(value_in_range, validator), **kwargs)


def signed(bits: int, validator=None, **kwargs):
    min_value = -(2**bits // 2)
    max_value = (2**bits // 2) - 1

    def value_in_range(_, __, value: int):
        if not min_value <= value <= max_value:
            raise ValueError(f"value must be between {min_value} and {max_value}")
    
    return attribute(getattr(construct, f"Int{bits}sl"), int,
        validator=_validator_maybe(value_in_range, validator), **kwargs)


u8 = partial(unsigned, 8)
u16 = partial(unsigned, 16)
u32 = partial(unsigned, 32)
u64 = partial(unsigned, 64)

i8 = partial(signed, 8)
i16 = partial(signed, 16)
i32 = partial(signed, 32)
i64 = partial(signed, 64)

string = partial(attribute, construct.PascalString(construct.Int16ul, "utf8"), str)

data = partial(attribute, construct.Prefixed(construct.Int32ul, construct.GreedyBytes), bytes)

class FileMode(enum.IntFlag):
    dir = 1 << 31
    append = 1 << 30
    excl = 1 << 29
    auth = 1 << 27
    tmp = 1 << 26
    owner_read = 1 << 8
    owner_write = 1 << 7
    owner_exec = 1 << 6
    group_read = 1 << 5
    group_write = 1 << 4
    group_exec = 1 << 3
    other_read = 1 << 2
    other_write = 1 << 1
    other_exec = 1 << 0

file_mode = partial(attribute, construct.FlagsEnum(construct.Int32ul, FileMode), FileMode)

class FileType(enum.IntFlag):
    dir = 1 << 7
    append = 1 << 6
    excl = 1 << 5
    auth = 1 << 3
    tmp = 1 << 2

file_type = partial(attribute, construct.FlagsEnum(construct.Int8ul, FileType), FileType)

def make_ctor(class_):
    return construct.Struct(
        *[x.name / x.metadata[CONSTRUCT] for x in attr.fields(class_)]
    )