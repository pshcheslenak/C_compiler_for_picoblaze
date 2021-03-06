"""This module defines and implements classes representing assembly commands.

The _ASMCommand object is the base class for most ASM commands. Some commands
inherit from _ASMCommandMultiSize or _JumpCommand instead.

"""


class _ASMCommand:
    """Base class for a standard ASMCommand, like `add` or `imul`.

    This class is used for ASM commands which take arguments of the same
    size.
    """

    name = None

    def __init__(self, dest=None, source=None, size=None):
        self.dest = dest.asm_str(size) if dest else None
        self.source = source.asm_str(size) if source else None
        self.size = size

    def __str__(self):
        s = "\t" + self.name
        if self.dest:
            s += " " + self.dest
        if self.source:
            s += ", " + self.source
        return s


class _ASMCommandMultiSize:
    """Base class for an ASMCommand which takes arguments of different sizes.

    For example, `movsx` and `movzx`.
    """

    name = None

    def __init__(self, dest, source, source_size, dest_size):
        self.dest = dest.asm_str(source_size)
        self.source = source.asm_str(dest_size)
        self.source_size = source_size
        self.dest_size = dest_size

    def __str__(self):
        s = "\t" + self.name
        if self.dest:
            s += " " + self.dest
        if self.source:
            s += ", " + self.source
        return s


class _JumpCommand:
    """Base class for jump commands."""

    name = None

    def __init__(self, target):
        self.target = target

    def __str__(self):
        s = "\t" + self.name + " " + self.target
        return s


class Comment:
    """Class for comments."""

    def __init__(self, msg):  # noqa: D102
        self.msg = msg

    def __str__(self):  # noqa: D102
        # return "\t// " + self.msg
        if self.msg == "LABEL":
            return ""
        return "\t; " + self.msg


class Label:
    """Class for label."""

    def __init__(self, label):  # noqa: D102
        self.label = label

    def __str__(self):  # noqa: D102
        return self.label + ":"


class Lea:
    """Class for lea command."""

    name = "lea"

    def __init__(self, dest, source):  # noqa: D102
        self.dest = dest
        self.source = source

    def __str__(self):  # noqa: D102
        return ("\t" + self.name + " " + self.dest.asm_str(8) + ", "
                "" + self.source.asm_str(0))

class Jump(_JumpCommand): name = "jump"

class JumpZ(_JumpCommand): name = "jump z"

class JumpNZ(_JumpCommand): name = "jump nz"

class JumpC(_JumpCommand): name = "jump c"

class JumpNC(_JumpCommand): name = "jump nc"

class Ja(_JumpCommand): name = "jump c"

class Jbe(_JumpCommand): name = "jump nc"


class Load(_ASMCommand): name = "load"


class Add(_ASMCommand): name = "add"
class Addcy(_ASMCommand): name = "addcy"

class Sub(_ASMCommand): name = "sub"
class Subcy(_ASMCommand): name = "subcy"


class Neg(_ASMCommand): name = "neg"  # noqa: D101


class Not(_ASMCommand): name = "not"  # noqa: D101


class Div(_ASMCommand): name = "div"  # noqa: D101


class Imul(_ASMCommand): name = "imul"  # noqa: D101


class Idiv(_ASMCommand): name = "idiv"  # noqa: D101


class And(_ASMCommand): name = "and"

class Or(_ASMCommand): name = "or"

class Xor(_ASMCommand): name = "xor"


class Compare(_ASMCommand): name = "compare"


class Call(_ASMCommand): name = "call"

class CallZ(_ASMCommand): name = "call z"

class CallNZ(_ASMCommand): name = "call nz"

class CallC(_ASMCommand): name = "call c"

class CallNC(_ASMCommand): name = "call nz"


class Return(_ASMCommand): name = "return"

class ReturnZ(_ASMCommand): name = "return z"

class ReturnNZ(_ASMCommand): name = "return nz"

class ReturnC(_ASMCommand): name = "return c"

class ReturnNC(_ASMCommand): name = "return nc"

class Sr0(_ASMCommandMultiSize): name = "sr0"

class Sr1(_ASMCommandMultiSize): name = "sr1"

class Sra(_ASMCommandMultiSize): name = "sra"

class Srx(_ASMCommandMultiSize): name = "srx"


class Sl0(_ASMCommandMultiSize): name = "sl0"

class Sl1(_ASMCommandMultiSize): name = "sl1"

class Sla(_ASMCommandMultiSize): name = "sla"

class Slx(_ASMCommandMultiSize): name = "slx"
