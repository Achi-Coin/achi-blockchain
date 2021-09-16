from typing import Union
from achi.types.full_block import FullBlock
from achi.types.unfinished_block import UnfinishedBlock
from achi.util.ints import uint32
from achi.util.errors import Err


def validate_checkpoints(block: Union[FullBlock, UnfinishedBlock], height: uint32):
    if height == 155555:
         # First checkpoint
        if block.header_hash != bytes.fromhex("f28ae8a5ae80e7bb489cf45a5dca7a3d4b0bbd72b2f65626727bf427fcf2da87"):
            return Err.INVALID_HEIGHT

    return None
