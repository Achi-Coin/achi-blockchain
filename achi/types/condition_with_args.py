from dataclasses import dataclass
from typing import List

from achi.types.condition_opcodes import ConditionOpcode
from achi.util.streamable import Streamable, streamable


@dataclass(frozen=True)
@streamable
class ConditionWithArgs(Streamable):
    """
    This structure is used to store parsed ALVM conditions
    Conditions in ALVM have either format of (opcode, var1) or (opcode, var1, var2)
    """

    opcode: ConditionOpcode
    vars: List[bytes]
