from dataclasses import dataclass

from achi.types.blockchain_format.coin import Coin
from achi.types.blockchain_format.sized_bytes import bytes32
from achi.util.ints import uint32, uint64
from achi.util.streamable import Streamable, streamable


@dataclass(frozen=True)
@streamable
class StakerRecord(Streamable):
    """
    These are values that correspond to a Staker.
    """

    coin: Coin
    confirmed_block_index: uint32
    spent_block_index: uint32
    spent: bool
    coinbase: bool
    puzzle_hash: bytes32
    timestamp: uint64  # Timestamp of the block at height confirmed_block_index
    name: bytes32

    def name(self):
        return self.name