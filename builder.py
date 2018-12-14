import attr
import construct
import enum as _enum
import typing
from functools import partial


CONSTRUCT = "__construct"


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
    max_value = 2 ** bits - 1

    def value_in_range(_, __, value: int):
        if not 0 <= value <= max_value:
            raise ValueError(f"value must be between 0 and {max_value}")

    return attribute(
        getattr(construct, f"Int{bits}ul"),
        int,
        validator=_validator_maybe(value_in_range, validator),
        **kwargs,
    )


def signed(bits: int, validator=None, **kwargs):
    min_value = -(2 ** bits // 2)
    max_value = (2 ** bits // 2) - 1

    def value_in_range(_, __, value: int):
        if not min_value <= value <= max_value:
            raise ValueError(f"value must be between {min_value} and {max_value}")

    return attribute(
        getattr(construct, f"Int{bits}sl"),
        int,
        validator=_validator_maybe(value_in_range, validator),
        **kwargs,
    )


u8 = partial(unsigned, 8)
u16 = partial(unsigned, 16)
u32 = partial(unsigned, 32)
u64 = partial(unsigned, 64)

i8 = partial(signed, 8)
i16 = partial(signed, 16)
i32 = partial(signed, 32)
i64 = partial(signed, 64)

string = partial(attribute, construct.PascalString(construct.Int16ul, "utf8"), str)

data = partial(
    attribute, construct.Prefixed(construct.Int32ul, construct.GreedyBytes), bytes
)


def enum(constructor, type, **kwargs):
    return attribute(constructor, type, converter=type, **kwargs)


def struct(type, **kwargs):
    return attribute(type._construct, type, converter=lambda x: type(**x), **kwargs)


def constructify(class_):
    """
    A decorator that assembles the individual field constructs into one Struct construct.
    """
    class_._construct = construct.Struct(
        x.name / x.metadata[CONSTRUCT] for x in attr.fields(class_)
    )
    return class_
