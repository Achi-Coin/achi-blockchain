from typing import Tuple

import aiosqlite

from achi.consensus.blockchain import Blockchain
from achi.consensus.constants import ConsensusConstants
from achi.full_node.block_store import BlockStore
from achi.full_node.coin_store import CoinStore
from achi.util.db_wrapper import DBWrapper
from achi.consensus.block_rewards import staking_rules


async def create_ram_blockchain(consensus_constants: ConsensusConstants) -> Tuple[aiosqlite.Connection, Blockchain]:
    connection = await aiosqlite.connect(":memory:")
    db_wrapper = DBWrapper(connection)
    block_store = await BlockStore.create(db_wrapper)
    coin_store = await CoinStore.create(db_wrapper)
    staker_store = await StakerStore.create(db_wrapper, staking_rules)    
    blockchain = await Blockchain.create(coin_store, block_store, staker_store, consensus_constants)
    return connection, blockchain
