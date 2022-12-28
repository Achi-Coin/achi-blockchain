from typing import List, Optional

import aiosqlite

from achi.types.blockchain_format.coin import Coin
from achi.types.staker_record import StakerRecord
from achi.types.staker_winner import StakerWinner
from achi.types.blockchain_format.sized_bytes import bytes32
from achi.types.full_block import FullBlock
from achi.util.db_wrapper import DBWrapper
from achi.util.ints import uint32, uint64
from achi.util.lru_cache import LRUCache
from achi.consensus.block_rewards import _sten_per_achi
from achi.util.bech32m import encode_puzzle_hash
from struct import unpack
from sortedcontainers import SortedList
import logging

log = logging.getLogger(__name__)

class StakerStore:
    """
    This object handles StakerRecords in DB.
    """

    staker_db: aiosqlite.Connection
    staker_winner_cache: LRUCache
    coin_cache: LRUCache
    cache_size: uint32
    db_wrapper: DBWrapper

    @classmethod
    async def create(cls, db_wrapper: DBWrapper, rules, cache_size: uint32 = uint32(60000)):
        self = cls()

        assert(len(rules) == 3)

        self.rules = rules
        self.stakers: List[SortedList[StakerRecord]] = []
        self.non_stakers: List[SortedList[StakerRecord]] = []

        for i in range(3):
            self.stakers.append(SortedList(key=lambda x: x.name))
            self.non_stakers.append(SortedList(key=lambda x: x.name))

        self.cache_size = cache_size
        self.db_wrapper = db_wrapper
        self.staker_db = db_wrapper.db
        await self.staker_db.execute("pragma journal_mode=wal")
        await self.staker_db.execute("pragma synchronous=2")

        for stage in range(1, len(self.rules) + 1):
            await self.staker_db.execute(
                (
                    f"CREATE TABLE IF NOT EXISTS staker_record{stage}(" 
                    " coin_name text PRIMARY KEY,"
                    " confirmed_index bigint,"
                    " spent_index bigint,"
                    " spent int,"
                    " coinbase int,"
                    " puzzle_hash text,"
                    " coin_parent text,"
                    " amount blob,"
                    " timestamp bigint)"
                )
            )

            # Useful for reorg lookups
            await self.staker_db.execute(
                f"CREATE INDEX IF NOT EXISTS staker_confirmed_index{stage} on staker_record{stage}(confirmed_index)"
            )

            await self.staker_db.execute(
                f"CREATE INDEX IF NOT EXISTS staker_spent_index{stage} on staker_record{stage}(spent_index)")

            await self.staker_db.execute(
                f"CREATE INDEX IF NOT EXISTS staker_spent{stage} on staker_record{stage}(spent)")

        await self.staker_db.commit()

        self.staker_winner_cache = LRUCache(cache_size)
        self.coin_cache = LRUCache(cache_size)

        return self

    def dump_statistics(self):
        for stage in range(1, len(self.rules) + 1):
            log.info("[stage %d] %d stakers " % (stage, len(self.stakers[stage - 1]), ))
            log.info("[stage %d] %d non-stakers " % (stage, len(self.non_stakers[stage - 1]), ))

    def get_stakers_amount(self, stage):
        return len(list(filter(lambda f: not f.spent, self.stakers[stage])))

    async def load(self) -> None:
        initial : bool = True

        for stage in range(1, len(self.rules) + 1):
            cursor = await self.staker_db.execute("SELECT coin_name, confirmed_index, spent_index, spent, coinbase, "
                f"puzzle_hash, coin_parent, amount, timestamp from staker_record{stage}")

            rows = await cursor.fetchall()
            await cursor.close()

            for row in rows:
                initial = False

                coin = Coin(parent_coin_info=bytes32(bytes.fromhex(row[6])), puzzle_hash=bytes32(bytes.fromhex(row[5])), 
                    amount=uint64.from_bytes(row[7]))

                record = StakerRecord(coin=coin, confirmed_block_index=row[1], spent_block_index=row[2], 
                    spent=row[3], coinbase=row[4], puzzle_hash=bytes32(bytes.fromhex(row[5])), timestamp=row[8],
                    name=coin.name())

                if record.spent:
                    self.non_stakers[stage - 1].add(record)
                else:
                    self.stakers[stage - 1].add(record)

                self.coin_cache.put(coin.name(), coin)

            log.info("[stage %d] %d stakers were loaded " % (stage, len(self.stakers[stage - 1]), ))
            log.info("[stage %d] %d non-stakers were loaded " % (stage, len(self.non_stakers[stage - 1]), ))

        if initial:
            await self.import_stakers()

    async def import_stakers(self):
        limit = 100_000
        index = 0
        cursor = await self.staker_db.execute("SELECT coin_name, confirmed_index, spent_index, spent, coinbase, "
                "puzzle_hash, coin_parent, amount, timestamp from coin_record")

        log.info("Fetching coins...")
        while True:
            log.info("%d coins are fetched" % (index+limit, ))
            rows = await cursor.fetchmany(limit)
            if len(rows) == 0:
                break
            index += limit
            for row in rows:
                coin = Coin(parent_coin_info=bytes32(bytes.fromhex(row[6])), puzzle_hash=bytes32(bytes.fromhex(row[5])), 
                    amount=uint64.from_bytes(row[7]))
                if await self._is_staker_coin(coin):
                    height = row[1]

                    for stage in range(0, len(self.rules)):
                        start_height = self.rules[stage][0]
                        staking_limit = self.rules[stage][1]

                        if height < start_height and await self._is_staker_coin_valid(coin, staking_limit):
                            staker = StakerRecord(coin=coin, confirmed_block_index=row[1], spent_block_index=row[2], 
                                spent=row[3], coinbase=row[4], puzzle_hash=bytes32(bytes.fromhex(row[5])), timestamp=row[8],
                                name=coin.name())
                            log.info("Staker was found at %d stage %d" % (staker.confirmed_block_index, stage+1))
                            await self._add_staker_record(staker, stage + 1, False)

        await cursor.close()

        await self.staker_db.commit()

        self.dump_statistics()

    async def _is_staker_coin(self, coin: Coin):
        addr = encode_puzzle_hash(coin.puzzle_hash, 'ach')

        if not addr.startswith("ach1stake"):
                return False

        return True

    async def _is_staker_coin_valid(self, coin: Coin, staking_limit):
        amount = coin.amount / _sten_per_achi
        if amount < staking_limit:
            return False

        return True

    async def new_block(self, block: FullBlock, tx_additions: List[Coin], tx_removals: List[bytes32]):
        log.debug(f"staker new_block {block.height}")

        if block.is_transaction_block():
            assert block.foliage_transaction_block is not None

            for coin in tx_additions:
                if not await self._is_staker_coin(coin):
                    continue

                for stage in range(0, len(self.rules)):
                    start_height = self.rules[stage][0]
                    staking_limit = self.rules[stage][1]

                    if block.height < start_height and await self._is_staker_coin_valid(coin, staking_limit):
                        log.info("Staker was found at %d stage %d" % (block.height, stage+1))
                        record: StakerRecord = StakerRecord(
                            coin=coin,
                            confirmed_block_index=block.height,
                            spent_block_index=uint32(0),
                            spent=False,
                            coinbase=False,
                            puzzle_hash=coin.puzzle_hash,
                            timestamp=block.foliage_transaction_block.timestamp,
                            name=coin.name()
                        )
                        await self._add_staker_record(record, stage + 1, False)

            for coin in tx_removals:
                c = self.coin_cache.get(coin)
                if c is None:
                    continue

                if not await self._is_staker_coin(c):
                    continue

                log.info("Staker was removed at %d" % (block.height, ))
                await self._set_spent(coin, block.height)

    async def rollback_to_block(self, block_index: int):
        """
        Please note that block_index can be negative, in this case everything is rolled back
        """

        log.info(f"staker rollback_to_block {block_index}")
        for stage in range(0, len(self.rules)):
            delete_queue: List[StakerRecord] = []
            add_queue: List[StakerRecord] = []

            for i in range(0, len(self.stakers[stage])):
                staker = self.stakers[stage][i]

                if int(staker.confirmed_block_index) > block_index:
                    delete_queue.append(staker)

            for i in range(0, len(self.non_stakers[stage])):
                staker = self.non_stakers[stage][i]

                if int(staker.confirmed_block_index) > block_index:
                    delete_queue.append(staker)

                elif int(staker.spent_block_index) > block_index:
                    new_staker = StakerRecord(
                     coin=staker.coin,
                     confirmed_block_index=staker.confirmed_block_index,
                     spent_block_index=uint32(0),
                     spent=False,
                     coinbase=staker.coinbase,
                     puzzle_hash=staker.puzzle_hash,
                     timestamp=staker.timestamp,
                     name=staker.coin.name())

                    add_queue.append(new_staker)
                    delete_queue.append(staker)

            for staker in delete_queue:
                self.stakers[stage].discard(staker)
                self.non_stakers[stage].discard(staker)

                coin = self.coin_cache.get(staker.name)
                if not coin is None:
                    self.coin_cache.remove(staker.name) 

            for staker in add_queue:
                if staker.spent:
                    self.non_stakers[stage].add(staker)
                else:
                    self.stakers[stage].add(staker)

                self.coin_cache.put(staker.name, staker.coin)

        # Delete from storage
        for stage in range(1, len(self.rules) + 1):
            c1 = await self.staker_db.execute(f"DELETE FROM staker_record{stage} WHERE confirmed_index>?", (block_index,))
            await c1.close()

            c2 = await self.staker_db.execute(
                f"UPDATE staker_record{stage} SET spent_index = 0, spent = 0 WHERE spent_index>?",
                (block_index,),
            )
            await c2.close()

        delete_queue: List[int] = []
        for height, item in list(self.staker_winner_cache.cache.items()):
            if height > block_index + 1:
                delete_queue.append(height)

        for height in delete_queue:
            self.staker_winner_cache.remove(height)

    # Store StakerRecord in DB
    async def _add_staker_record(self, record: StakerRecord, stage: int, allow_replace: bool) -> None:
        cursor = await self.staker_db.execute(
            f"INSERT {'OR REPLACE ' if allow_replace else ''}INTO staker_record{stage} (coin_name, confirmed_index, spent_index, "
                "spent, coinbase, puzzle_hash, coin_parent, amount, timestamp) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                record.coin.name().hex(),
                record.confirmed_block_index,
                record.spent_block_index,
                int(record.spent),
                int(record.coinbase),
                str(record.coin.puzzle_hash.hex()),
                str(record.coin.parent_coin_info.hex()),
                bytes(record.coin.amount),
                record.timestamp,
            ),
        )
        await cursor.close()

        if record.spent:
            self.non_stakers[stage - 1].add(record)
        else:
            self.stakers[stage - 1].add(record)

        self.coin_cache.put(record.name, record.coin)


    # Update staker_record to be spent in DB
    async def _set_spent(self, coin_name: bytes32, index: uint32):
        for stage in range(1, len(self.rules) + 1):
            c = await self.staker_db.execute(
                f"UPDATE staker_record{stage} SET spent_index = ?, spent = 1 where coin_name = ?",
                (index,
                coin_name.hex()))

            await c.close()

            for idx, staker in enumerate(self.stakers[stage - 1]):
                if staker.name == coin_name:
                    new_staker = StakerRecord(
                        coin=staker.coin,
                        confirmed_block_index=staker.confirmed_block_index,
                        spent_block_index=index,
                        spent=True,
                        coinbase=staker.coinbase,
                        puzzle_hash=staker.puzzle_hash,
                        timestamp=staker.timestamp,
                        name=staker.coin.name())

                    self.stakers[stage - 1].remove(staker)
                    self.non_stakers[stage - 1].add(new_staker)
                    break

    async def _add_staker_winner_record(self, record: StakerWinner, allow_replace: bool) -> None:
        cursor = await self.staker_db.execute(
            f"INSERT {'OR REPLACE ' if allow_replace else ''}INTO staker_winner(height, winner_puzzle_hash,"
                " total_stakers_amount) VALUES(?, ?, ?)",
            (
                record.height,
                str(record.puzzle_hash.hex()),
                record.stakers_amount
            ),
        )
        await cursor.close()

        self.staker_winner_cache.put(record.height, record)

    def get_stage(self, height: uint32) -> int:
        assert(len(self.rules) == 3)

        if height < self.rules[0][0]:
            return 0

        if height >= self.rules[0][0] and height < self.rules[1][0]:
            return 1

        if height >= self.rules[1][0] and height < self.rules[2][0]:
            return 2

        if height >= self.rules[2][0]:
            return 3

        return -1

    def make_winner(self, header_hash: bytes32, height: uint32) -> Optional[StakerWinner]:
        stage = self.get_stage(height)

        if stage < 2:
            return None

        stakers = self.stakers[stage - 2]

        amount = len(stakers)
        if amount < 1:
            return None

        val = unpack(">I", header_hash[-4:])[0]
        winner = stakers[val % amount]

        return StakerWinner(height=height, puzzle_hash=winner.coin.puzzle_hash, stakers_amount=amount)

    def get_winner_record_sync(self, header_hash: bytes32, height: uint32) -> Optional[StakerWinner]:
        log.debug(f"get_winner_record_sync height={height}")

        winner = self.make_winner(header_hash, height)

        if not winner is None:
            log.debug(f"get_winner_record_sync winner={winner.puzzle_hash}, amount={winner.stakers_amount}")
        else:
            log.debug(f"get_winner_record_sync winner=None")

        return winner

    async def get_winner_record(self, height: uint32) -> Optional[StakerWinner]:
        log.debug(f"get_winner_record height={height}")

        cached = self.staker_winner_cache.get(height)
        if cached is not None:
            return cached
        cursor = await self.staker_db.execute("SELECT height, winner_puzzle_hash, total_stakers_amount from "
            "staker_winner WHERE height=?", (height,))
        row = await cursor.fetchone()
        await cursor.close()
        if row is not None:
            record = StakerWinner(height=row[0], puzzle_hash=bytes32(bytes.fromhex(row[1])), stakers_amount=row[2])
            self.staker_winner_cache.put(record.height, record)
            return record
        return None
