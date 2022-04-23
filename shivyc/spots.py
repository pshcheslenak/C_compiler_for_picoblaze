"""The Spot object definition and and some predefined spots, like registers."""


class Spot:
    """Spot in the machine where an IL value can be.

    spot_type (enum) - One of the values below describing the general type of
    spot this is.
    detail - Additional information about this spot. The this attribute's type
    and meaning depend on the spot_type; see below for more.

    """

    def __init__(self, detail):
        """Initialize a spot.

        `detail` should uniquely represent this Spot for this specific spot
        type, because it will be used for hashing and equality testing.
        """
        self.detail = detail

    def asm_str(self, size):
        """Make the ASM form of this spot, for the given size in bytes.

        This function raises NotImplementedError for unsupported sizes.

        Examples:
            spots.RAX.asm_str(4) -> "eax"
            spots.RAX.asm_str(8) -> "rax"
            spot(STACK, -16).asm_str(4) -> "DWORD [rbp-16]"
            spot(LITERAL, 14).asm_str(4) -> "14"

        size (int) - Size in bytes of the data stored at this spot.
        return (str) - ASM form of this spot.

        """
        raise NotImplementedError

    def rbp_offset(self):
        """Return this spot's offset from RBP.

        If this is a memory spot which resides at a certain negative offset
        away from RBP, then return that offset. This is used by the register
        allocator to figure out how much memory to allocate for this spot.

        If this is not a memory spot relative to RBP, just return 0.
        """
        return 0

    def shift(self, chunk, count=None):
        """Return a new spot shifted relative to this one.

        For non-memory spots, this function returns itself and throws an
        error if given chunk != 0 or count != None.
        """
        if chunk or count:
            raise NotImplementedError("cannot shift this spot type")
        return self

    def __repr__(self):  # pragma: no cover
        return self.detail

    def __eq__(self, other):
        """Test equality by comparing Spot type and detail."""
        if self.__class__.__name__ != other.__class__.__name__:
            return False

        return self.detail == other.detail

    def __hash__(self):
        """Hash based on type and detail."""
        return hash((self.__class__.__name__, self.detail))


class RegSpot(Spot):
    """Spot representing a machine register."""

    reg_map = {"s0": "s0",
               "s1": "s1",
               "s2": "s2",
               "s3": "s3",
               "s4": "s4",
               "s5": "s5",
               "s6": "s6",
               "s7": "s7",
               "s8": "s8",
               "s9": "s9",
               "sA": "sA",
               "sB": "sB",
               "sC": "sC",
               "sD": "sD",
               "sE": "sE",
               "sF": "sF"}

    def __init__(self, name):
        """Initialize this spot.

        `name` is the string representation of the 64-bit register (e.g.
        "s0").
        """
        super().__init__(name)
        self.name = name

    def asm_str(self, size):  # noqa D102
        return self.reg_map[self.name]


class MemSpot(Spot):
    """Spot representing a region in memory, like on stack or .data section.

    `base` can be either a string or a Spot. The string form is used when
    this spot represents an external variable. The Spot form is used when
    this spot represents an offset in memory, like [rbp-5].
    """

    # size_map = {1: "BYTE PTR ",
    #             2: "WORD PTR ",
    #             4: "DWORD PTR ",
    #             8: "QWORD PTR "}

    def __init__(self, base, offset=0, chunk=0, count=None):  # noqa D102
        super().__init__((base, offset, chunk, count))

        self.base = base
        self.offset = offset
        self.chunk = chunk
        self.count = count

    def asm_str(self, size):  # noqa D102
        if isinstance(self.base, Spot):
            base_str = self.base.asm_str(0)
        else:
            base_str = self.base

        total_offset = self.offset
        if not self.count:
            total_offset = self.offset + self.chunk

        if total_offset == 0:
            simple = base_str
        elif total_offset > 0:
            simple = f"{base_str}+{total_offset}"
        else:  # total_offset < 0
            simple = f"{base_str}-{-total_offset}"

        if self.count and self.chunk > 0:
            final = f"{simple}+{self.chunk}*{self.count.asm_str(8)}"
        elif self.count and self.chunk < 0:
            final = f"{simple}-{-self.chunk}*{self.count.asm_str(8)}"
        else:
            final = simple

        # size_desc = self.size_map.get(size, "")
        # return f"{size_desc}[{final}]"
        return f"[{final}]"

    # def rbp_offset(self):  # noqa D102
    #     if self.base == RBP:
    #         return -self.offset
    #     else:
    #         return 0

    def shift(self, chunk, count=None):  # noqa D102
        """Return a new memory spot shifted relative to this one.

        chunk - A Python integer representing the size of each chunk of offset
        count - If provided, a register spot storing the number of chunks to
        be offset. If this value is provided, then `chunk` must be in {1, 2,
        4, 8}.
        """
        if count and self.count:
            raise NotImplementedError("cannot shift by count")

        if count:
            new_offset = self.offset + self.chunk
            new_chunk = chunk
            new_count = count
        else:  # no count given
            new_offset = self.offset + chunk
            new_chunk = self.chunk
            new_count = self.count

        return MemSpot(self.base, new_offset, new_chunk, new_count)


class LiteralSpot(Spot):
    """Spot representing a literal value.

    This is a bit of a hack, since a literal value isn't /really/ a storage
    spot. The value attribute is the integer representation of the value of
    this literal.
    """

    def __init__(self, value):
        super().__init__(value)
        self.value = value

    def asm_str(self, size):  # noqa D102
        return str(self.value)


# RBX is callee-saved, which is still unsupported
# RBX = RegSpot("s1")

S0 = RegSpot("s0")
S1 = RegSpot("s1")
S2 = RegSpot("s2")
S3 = RegSpot("s3")
S4 = RegSpot("s4")
S5 = RegSpot("s5")
S6 = RegSpot("s6")
S7 = RegSpot("s7")
S8 = RegSpot("s8")
S9 = RegSpot("s9")
SA = RegSpot("sA")
SB = RegSpot("sB")
SC = RegSpot("sC")
SD = RegSpot("sD")
SE = RegSpot("sE")
SF = RegSpot("sF")

registers = [S0, S1, S2, S3, S4, S5, S6, S7,
             S8, S9, SA ,SB, SC, SD, SE, SF]


