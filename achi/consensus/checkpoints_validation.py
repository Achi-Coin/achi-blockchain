from typing import Union
from achi.types.full_block import FullBlock
from achi.types.unfinished_block import UnfinishedBlock
from achi.util.ints import uint32
from achi.util.errors import Err


def validate_checkpoints(block: Union[FullBlock, UnfinishedBlock], height: uint32):
    if height == 155_555:
         # First checkpoint
        if block.header_hash != bytes.fromhex("f28ae8a5ae80e7bb489cf45a5dca7a3d4b0bbd72b2f65626727bf427fcf2da87"):
            return Err.INVALID_HEIGHT

    if height == 313_131:
         # Checkpoint #2
        if block.header_hash != bytes.fromhex("b165503620fd42ab9e35753db6bb21f7ba410e39e72dd06983702c96ea08531b"):
            return Err.INVALID_HEIGHT

    if height == 500_000:
         # Checkpoint #3
        if block.header_hash != bytes.fromhex("b470f417c29466fef4ec36172c65bab5f1d6a9a8157c6a17017f725ed1e65b83"):
            return Err.INVALID_HEIGHT

    if height == 1_000_000:
         # Checkpoint #4
        if block.header_hash != bytes.fromhex("f9a5b0f09281829f3a10def19e7120b125d58a3ebd1fbc7ba6c03445f93359b7"):
            return Err.INVALID_HEIGHT

    if height == 1_500_000:
         # Checkpoint #5
        if block.header_hash != bytes.fromhex("fd8f4d0100517f3ab06a96f93f1aa6f5d674d20edee1126f6c88066b3109d765"):
            return Err.INVALID_HEIGHT

    if height == 2_000_000:
         # Checkpoint #6
        if block.header_hash != bytes.fromhex("0905305613f6e0351edd8d7fd22273b22dbb26deb0945b815606fe752ab220ab"):
            return Err.INVALID_HEIGHT

    if height == 2_300_000:
         # Checkpoint #7
        if block.header_hash != bytes.fromhex("ceafe212e2f8ec304658de580f0f59a694bcdf4db28623aa83d83e904c8ab84c"):
            return Err.INVALID_HEIGHT

    return None
