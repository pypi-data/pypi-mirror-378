# -*- coding: utf-8 -*-
import json
import struct
import time
from binascii import hexlify, unhexlify

# Move calendar import to avoid circular import issue in Python 3.13
from datetime import datetime

# Import calendar only when needed to avoid circular imports
timeformat = "%Y-%m-%dT%H:%M:%S%Z"


def varint(n):
    """Varint encoding."""
    data = b""
    while n >= 0x80:
        data += bytes([(n & 0x7F) | 0x80])
        n >>= 7
    data += bytes([n])
    return data


def varintdecode(data):
    """Varint decoding."""
    shift = 0
    result = 0
    for b in bytes(data):
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return result


def variable_buffer(s):
    """Encodes variable length buffer."""
    return varint(len(s)) + s


def JsonObj(data):
    """Returns json object from data."""
    return json.loads(str(data))


class Uint8(object):
    """Uint8."""

    def __init__(self, d):
        """init."""
        self.data = int(d)

    def __bytes__(self):
        """Returns bytes."""
        return struct.pack("<B", self.data)

    def __str__(self):
        """Returns str"""
        return "%d" % self.data


class Int16(object):
    """Int16."""

    def __init__(self, d):
        """init."""
        self.data = int(d)

    def __bytes__(self):
        """Returns bytes."""
        return struct.pack("<h", int(self.data))

    def __str__(self):
        return "%d" % self.data


class Uint16(object):
    def __init__(self, d):
        self.data = int(d)

    def __bytes__(self):
        """Returns bytes."""
        return struct.pack("<H", self.data)

    def __str__(self):
        return "%d" % self.data


class Uint32(object):
    def __init__(self, d):
        self.data = int(d)

    def __bytes__(self):
        """Returns bytes."""
        return struct.pack("<I", self.data)

    def __str__(self):
        """Returns data as string."""
        return "%d" % self.data


class Uint64(object):
    def __init__(self, d):
        self.data = int(d)

    def __bytes__(self):
        """Returns bytes."""
        return struct.pack("<Q", self.data)

    def __str__(self):
        """Returns data as string."""
        return "%d" % self.data


class Varint32(object):
    def __init__(self, d):
        self.data = int(d)

    def __bytes__(self):
        """Returns bytes."""
        return varint(self.data)

    def __str__(self):
        """Returns data as string."""
        return "%d" % self.data


class Int64(object):
    def __init__(self, d):
        self.data = int(d)

    def __bytes__(self):
        """Returns bytes."""
        return struct.pack("<q", self.data)

    def __str__(self):
        """Returns data as string."""
        return "%d" % self.data


class HexString(object):
    def __init__(self, d):
        self.data = d

    def __bytes__(self):
        """Returns bytes representation."""
        d = bytes(unhexlify(bytes(self.data, "ascii")))
        return varint(len(d)) + d

    def __str__(self):
        """Returns data as string."""
        return "%s" % str(self.data)


class String(object):
    def __init__(self, d):
        self.data = d

    def __bytes__(self):
        """Returns bytes representation."""
        d = self.unicodify()
        return varint(len(d)) + d

    def __str__(self):
        """Returns data as string."""
        return "%s" % str(self.data)

    def unicodify(self):
        r = []
        for s in self.data:
            o = ord(s)
            if (o <= 7) or (o == 11) or (o > 13 and o < 32):
                r.append("u%04x" % o)
            elif o == 8:
                r.append("b")
            elif o == 9:
                r.append("\t")
            elif o == 10:
                r.append("\n")
            elif o == 12:
                r.append("f")
            elif o == 13:
                r.append("\r")
            else:
                r.append(s)
        return bytes("".join(r), "utf-8")


class Bytes(object):
    def __init__(self, d):
        self.data = d

    def __bytes__(self):
        """Returns data as bytes."""
        d = unhexlify(bytes(self.data, "utf-8"))
        return varint(len(d)) + d

    def __str__(self):
        """Returns data as string."""
        return str(self.data)


class Hash(Bytes):
    def json(self):
        return str(self.data)

    def __bytes__(self):
        return unhexlify(bytes(self.data, "utf-8"))


class Ripemd160(Hash):
    def __init__(self, a):
        assert len(a) == 40, "Require 40 char long hex"
        super().__init__(a)


class Sha1(Hash):
    def __init__(self, a):
        assert len(a) == 40, "Require 40 char long hex"
        super().__init__(a)


class Sha256(Hash):
    def __init__(self, a):
        assert len(a) == 64, "Require 64 char long hex"
        super().__init__(a)


class Void(object):
    def __init__(self):
        pass

    def __bytes__(self):
        """Returns bytes representation."""
        return b""

    def __str__(self):
        """Returns data as string."""
        return ""


class Array(object):
    def __init__(self, d):
        self.data = d
        self.length = Varint32(len(self.data))

    def __bytes__(self):
        """Returns bytes representation."""
        return bytes(self.length) + b"".join([bytes(a) for a in self.data])

    def __str__(self):
        """Returns data as string."""
        r = []
        for a in self.data:
            try:
                if isinstance(a, String):
                    r.append(str(a))
                else:
                    r.append(JsonObj(a))
            except Exception:
                r.append(str(a))
        return json.dumps(r)


class PointInTime(object):
    def __init__(self, d):
        self.data = d

    def __bytes__(self):
        """
        Return a 4-byte little-endian Unix timestamp for the stored point-in-time.

        If the instance holds a datetime, it is converted to a POSIX timestamp using UTC. If it holds a string, the string is parsed (with the module-level `timeformat` and "UTC" appended) and converted to a POSIX timestamp. The timestamp is encoded as a signed 32-bit little-endian integer when negative, otherwise as an unsigned 32-bit little-endian integer.
        """
        # Import lazily to avoid import-time cycles
        from calendar import timegm

        if isinstance(self.data, datetime):
            # Use UTC, not local time
            unixtime = timegm(self.data.utctimetuple())
        else:
            s = self.data
            # Accept ISO8601 'Z' suffix
            if isinstance(s, str) and s.endswith("Z"):
                s = s[:-1]
            unixtime = timegm(time.strptime((s + "UTC"), timeformat))
        if unixtime < 0:
            return struct.pack("<i", unixtime)
        return struct.pack("<I", unixtime)

    def __str__(self):
        """Returns data as string."""
        return self.data


class Signature(object):
    def __init__(self, d):
        self.data = d

    def __bytes__(self):
        """Returns bytes representation."""
        return self.data

    def __str__(self):
        """Returns data as string."""
        return json.dumps(hexlify(self.data).decode("ascii"))


class Bool(Uint8):  # Bool = Uint8
    def __init__(self, d):
        super(Bool, self).__init__(d)

    def __str__(self):
        """Returns data as string."""
        return json.dumps(True) if self.data else json.dumps(False)


class Set(Array):  # Set = Array
    def __init__(self, d):
        super(Set, self).__init__(d)


class Fixed_array(object):
    def __init__(self, d):
        raise NotImplementedError

    def __bytes__(self):
        """Returns bytes representation."""
        raise NotImplementedError

    def __str__(self):
        """Returns data as string."""
        raise NotImplementedError


class Optional(object):
    def __init__(self, d):
        self.data = d

    def __bytes__(self):
        """Returns data as bytes."""
        if not self.data:
            return bytes(Bool(0))
        else:
            return bytes(Bool(1)) + bytes(self.data)

    def __str__(self):
        """Returns data as string."""
        return str(self.data)

    def isempty(self):
        """Returns True if data is empty, False otherwise."""
        return not self.data


class Static_variant(object):
    def __init__(self, d, type_id, legacy_style=True):
        self.data = d
        self.type_id = type_id

        # `legacy_style = True` it means, that static variant is treated like an array, otherwise like an object
        self.legacy_style = legacy_style

    def __bytes__(self):
        """Returns bytes representation."""
        return varint(self.type_id) + bytes(self.data)

    def __str__(self):
        """Returns data as string."""
        if self.legacy_style:
            return json.dumps([self.type_id, self.data.json()])
        else:
            return json.dumps({"type": self.type_id, "value": self.data.json()})


class Map(object):
    def __init__(self, data):
        self.data = data

    def __bytes__(self):
        """Returns bytes representation."""
        b = b""
        b += varint(len(self.data))
        for e in self.data:
            b += bytes(e[0]) + bytes(e[1])
        return b

    def __str__(self):
        """Returns data as string."""
        r = []
        for e in self.data:
            r.append([str(e[0]), str(e[1])])
        return json.dumps(r)


class Id(object):
    def __init__(self, d):
        self.data = Varint32(d)

    def __bytes__(self):
        """Returns bytes representation."""
        return bytes(self.data)

    def __str__(self):
        """Returns data as string."""
        return str(self.data)


class Enum8(Uint8):
    # List needs to be provided by super class
    options = []

    def __init__(self, selection):
        if selection not in self.options or (
            isinstance(selection, int) and len(self.options) < selection
        ):
            raise ValueError("Options are {}. Given '{}'".format(str(self.options), selection))

        super(Enum8, self).__init__(self.options.index(selection))

    def __str__(self):
        """Returns data as string."""
        return str(self.options[self.data])
