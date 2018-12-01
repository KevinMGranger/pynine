from primitives import *
import attr

@attr.s
class Qid:
    type_ = file_type()
    version = u32()
    path = u64()