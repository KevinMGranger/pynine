from builder import *
import construct
import attr
import enum
from functools import partial


class FileType(enum.IntFlag):
    dir = 1 << 7
    append = 1 << 6
    excl = 1 << 5
    auth = 1 << 3
    tmp = 1 << 2


file_type = partial(enum, construct.Int8ul, FileType)


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


file_mode = partial(enum, construct.Int32ul, FileMode)


@constructify
@attr.s
class Qid:
    type_ = file_type()
    version = u32()
    path = u64()


@constructify
@attr.s
class Stat:
    type = u16()
    dev = u16()
    qid = struct(Qid)
    mode = file_mode()
    atime = u32()
    mtime = u32()
    length = u64()
    name = string()
    uid = string()
    gid = string()
    muid = string()


Stat._construct = construct.Prefixed(
    construct.Int16ul, construct.Prefixed(construct.Int16ul, Stat._construct)
)


# Tversion tag[2] msize[4] version[s]
# Rversion tag[2] msize[4] version[s]
@constructify
@attr.s
class Version:
    tag = u16()
    msize = u32()
    version = string()


Tversion = Version
Rversion = Version

# Tauth tag[2] afid[4] uname[s] aname[s]
@constructify
@attr.s
class Tauth:
    tag = u16()
    afid = u32()
    uname = string()
    aname = string()


# Rauth tag[2] aqid[13]
@constructify
@attr.s
class Rauth:
    tag = u16()
    aqid = struct(Qid)


# Rerror tag[2] ename[s]
@constructify
@attr.s
class Rerror:
    tag = u16()
    ename = string()


# Tflush tag[2] oldtag[2]
# Rflush tag[2]
# Tattach tag[2] fid[4] afid[4] uname[s] aname[s]
# Rattach tag[2] qid[13]
# Twalk tag[2] fid[4] newfid[4] nwname[2] nwname*(wname[s])
# Rwalk tag[2] nwqid[2] nwqid*(wqid[13])
# Topen tag[2] fid[4] mode[1]
# Ropen tag[2] qid[13] iounit[4]
# Topenfd tag[2] fid[4] mode[1]
# Ropenfd tag[2] qid[13] iounit[4] unixfd[4]
# Tcreate tag[2] fid[4] name[s] perm[4] mode[1]
# Rcreate tag[2] qid[13] iounit[4]
# Tread tag[2] fid[4] offset[8] count[4]
# Rread tag[2] count[4] data[count]
# Twrite tag[2] fid[4] offset[8] count[4] data[count]
# Rwrite tag[2] count[4]
# Tclunk tag[2] fid[4]
# Rclunk tag[2]
# Tremove tag[2] fid[4]
# Rremove tag[2]
# Tstat tag[2] fid[4]
# Rstat tag[2] stat[n]
# Twstat tag[2] fid[4] stat[n]
# Rwstat tag[2]


# size[4] Rattach tag[2] qid[13]
@constructify
@attr.s
class Rattach:
    tag = u16()
    qid = struct(Qid)


class MessageIDs(enum.Enum):
    Tversion = 100
    Rversion = 101

    Tauth = 102
    Rauth = 103

    Tattach = 104
    Rattach = 105

    Rerror = 107

    Tflush = 108
    Rflush = 109

    Twalk = 110
    Rwalk = 111

    Topen = 112
    Ropen = 113

    Tcreate = 114
    Rcreate = 115

    Tread = 116
    Rread = 117

    Twrite = 118
    Rwrite = 119

    Tclunk = 120
    Rclunk = 121

    Tremove = 122
    Rremove = 123

    Tstat = 124
    Rstat = 125

    Twstat = 126
    Rwstat = 127
