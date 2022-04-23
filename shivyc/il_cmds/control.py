"""IL commands for labels, jumps, and function calls."""

import asm_cmds as asm_cmds
import spots as spots
from il_cmds.base import ILCommand
from spots import LiteralSpot


class Label(ILCommand):
    """Label - Analogous to an ASM label."""

    def __init__(self, label): # noqa D102
        """The label argument is an string label name unique to this label."""
        self.label = label

    def inputs(self): # noqa D102
        return []

    def outputs(self): # noqa D102
        return []

    def label_name(self):  # noqa D102
        return self.label

    def make_asm(self, spotmap, home_spots, get_reg, asm_code): # noqa D102
        asm_code.add(asm_cmds.Label(self.label))


class Jump(ILCommand):
    """Jumps unconditionally to a label."""

    def __init__(self, label): # noqa D102
        self.label = label

    def inputs(self): # noqa D102
        return []

    def outputs(self): # noqa D102
        return []

    def targets(self): # noqa D102
        return [self.label]

    def make_asm(self, spotmap, home_spots, get_reg, asm_code): # noqa D102
        asm_code.add(asm_cmds.Jump(self.label))


class _GeneralJump(ILCommand):
    """General class for jumping to a label based on condition."""

    # ASM command to output for this jump IL command.
    # (asm_cmds.JumpZ for JumpZero and asm_cmds.JumpNZ for JumpNotZero)
    asm_cmd = None

    def __init__(self, cond, label): # noqa D102
        self.cond = cond
        self.label = label

    def inputs(self): # noqa D102
        return [self.cond]

    def outputs(self): # noqa D102
        return []

    def targets(self): # noqa D102
        return [self.label]

    def make_asm(self, spotmap, home_spots, get_reg, asm_code): # noqa D102
        size = self.cond.ctype.size

        if isinstance(spotmap[self.cond], LiteralSpot):
            r = get_reg()
            asm_code.add(asm_cmds.Load(r, spotmap[self.cond]))
            cond_spot = r
        else:
            cond_spot = spotmap[self.cond]

        zero_spot = LiteralSpot("0")
        asm_code.add(asm_cmds.Compare(cond_spot, zero_spot))
        asm_code.add(self.command(self.label))


class JumpZero(_GeneralJump):
    """Jumps to a label if given condition is zero."""

    command = asm_cmds.JumpZ


class JumpNotZero(_GeneralJump):
    """Jumps to a label if given condition is non zero."""

    command = asm_cmds.JumpNZ


class Return(ILCommand):
    """RETURN - returns the given value from function.

    If arg is None, then returns from the function without putting any value
    in the return register. Today, only supports values that fit in one
    register.
    """

    def __init__(self, arg=None): # noqa D102
        # arg must already be cast to return type
        self.arg = arg

    def inputs(self): # noqa D102
        return [self.arg]

    def outputs(self): # noqa D102
        return []

    def clobber(self):  # noqa D102
        return [spots.S0]

    def abs_spot_pref(self):  # noqa D102
        return {self.arg: [spots.S0]}

    def make_asm(self, spotmap, home_spots, get_reg, asm_code): # noqa D102
        if self.arg and spotmap[self.arg] != spots.S0:
            size = self.arg.ctype.size
            asm_code.add(asm_cmds.Load(spots.S0, spotmap[self.arg]))

        asm_code.add(asm_cmds.Return())


class Call(ILCommand):
    """Call a given function.

    func - Pointer to function
    args - Arguments of the function, in left-to-right order. Must match the
    parameter types the function expects.
    ret - If function has non-void return type, IL value to save the return
    value. Its type must match the function return value.
    """

    arg_regs = [spots.S0, spots.S1, spots.S2, spots.S3,
                spots.S4, spots.S5, spots.S6, spots.S7,
                spots.S8, spots.S9, spots.SA, spots.SB,
                spots.SC, spots.SD, spots.SE, spots.SF]

    def __init__(self, func, args, ret): # noqa D102
        self.func = func
        self.args = args
        self.ret = ret
        self.void_return = self.func.ctype.arg.ret.is_void()

        if len(self.args) > len(self.arg_regs):
            raise NotImplementedError("too many arguments")

    def inputs(self): # noqa D102
        return [self.func] + self.args

    def outputs(self): # noqa D102
        return [] if self.void_return else [self.ret]

    def clobber(self): # noqa D102
        # All caller-saved registers are clobbered by function call
        return [spots.S0, spots.S1, spots.S2, spots.S3,
                spots.S4, spots.S5, spots.S6, spots.S7,
                spots.S8, spots.S9, spots.SA, spots.SB,
                spots.SC, spots.SD, spots.SE, spots.SF]

    def abs_spot_pref(self): # noqa D102
        prefs = {} if self.void_return else {self.ret: [spots.S0]}
        # prefs = {} if self.void_return else self.func
        for arg, reg in zip(self.args, self.arg_regs):
            prefs[arg] = [reg]

        return prefs

    def abs_spot_conf(self): # noqa D102
        # We don't want the function pointer to be in the same register as
        # an argument will be placed into.
        return {self.func: self.arg_regs[0:len(self.args)]}

    def indir_write(self): # noqa D102
        return self.args

    def indir_read(self): # noqa D102
        return self.args

    def make_asm(self, spotmap, home_spots, get_reg, asm_code): # noqa D102
        func_spot = spotmap[self.func]

        func_size = self.func.ctype.size
        ret_size = self.func.ctype.arg.ret.size

        # Check if function pointer spot will be clobbered by moving the
        # arguments into the correct registers.
        if spotmap[self.func] in self.arg_regs[0:len(self.args)]:
            # Get a register which isn't one of the unallowed registers.
            # r = get_reg([], self.arg_regs[0:len(self.args)])
            r = self.func
            print("2", r)
            asm_code.add(asm_cmds.Load(r, spotmap[self.func]))
            func_spot = r

        for arg, reg in zip(self.args, self.arg_regs):
            if spotmap[arg] == reg:
                continue
            print("2", spotmap[arg])
            asm_code.add(asm_cmds.Load(reg, spotmap[arg]))
        print("4", spotmap[self.func])
        asm_code.add(asm_cmds.Call(func_spot))
        # asm_code.add(asm_cmds.Call(func))


        if not self.void_return and spotmap[self.ret] != spots.S0:
            asm_code.add(asm_cmds.Load(spotmap[self.ret], spots.S0))
