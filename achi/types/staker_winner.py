from dataclasses import dataclass

from achi.types.blockchain_format.sized_bytes import bytes32
from achi.util.ints import uint32
from achi.util.streamable import Streamable, streamable


@dataclass(frozen=True)
@streamable
class StakerWinner(Streamable):
    """
    Fields used to track winning Stakers.
    """

    height: uint32
    puzzle_hash: bytes32
    stakers_amount: uint32

