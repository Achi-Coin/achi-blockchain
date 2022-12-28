from achi.util.ints import uint32, uint64

# 1 Achi coin = 1,000,000,000 = 1 billion sten.
_sten_per_achi = 1_000_000_000
_blocks_per_day = 4608  # 32 * 6 * 24

period0 = 0
period1 = period0 + pow(2,  3)
period2 = period1 + pow(2,  4)
period3 = period2 + pow(2,  5)
period4 = period3 + pow(2,  6)
period5 = period4 + pow(2,  7)
period6 = period5 + pow(2,  8)
period7 = period6 + pow(2,  9)
period8 = period7 + pow(2, 10)

reward1 = pow(2, 15)
reward2 = pow(2, 14)
reward3 = pow(2, 13)
reward4 = pow(2, 12)
reward5 = pow(2, 11)
reward6 = pow(2, 10)
reward7 = pow(2,  9)
reward8 = pow(2,  8)
reward9 = pow(2,  7)

timelord_fraction = 0.02 / 100
pool_fraction = 7 / 8
farmer_fraction = 1 / 8

staking_rules = [(period5 * _blocks_per_day, 1_000_000.0),
                (period6 * _blocks_per_day, 1_000_000.0), 
                (period7 * _blocks_per_day, 1_000_000.0)]

def calculate_timelord_reward(height: uint32) -> uint64:
    if height == 0:
        return uint64(0)
    elif height < period1 * _blocks_per_day:
        return uint64(int(timelord_fraction * reward1 * _sten_per_achi))
    elif height < period2 * _blocks_per_day:
        return uint64(int(timelord_fraction * reward2 * _sten_per_achi))
    elif height < period3 * _blocks_per_day:
        return uint64(int(timelord_fraction * reward3 * _sten_per_achi))
    elif height < period4 * _blocks_per_day:
        return uint64(int(timelord_fraction * reward4 * _sten_per_achi))
    elif height < period5 * _blocks_per_day:
        return uint64(int(timelord_fraction * reward5 * _sten_per_achi))
    elif height < period6 * _blocks_per_day:
        return uint64(int(timelord_fraction * reward6 * _sten_per_achi))
    elif height < period7 * _blocks_per_day:
        return uint64(int(1 * _sten_per_achi))
    elif height < period8 * _blocks_per_day:
        return uint64(int(1 * _sten_per_achi))
    else:
        return uint64(int(1 * _sten_per_achi))

def calculate_staker_reward(height: uint32) -> uint64:
    if height < period6 * _blocks_per_day:
        return uint64(0)
    elif height < period7 * _blocks_per_day:
        return uint64(int(16 * _sten_per_achi))
    elif height < period8 * _blocks_per_day:
        return uint64(int(32 * _sten_per_achi))
    else:
        return uint64(int(64 * _sten_per_achi))


def calculate_pool_reward(height: uint32) -> uint64:
    if height == 0:
        return uint64(0)
    elif height < period1 * _blocks_per_day:
        return uint64(int(pool_fraction * reward1 * _sten_per_achi)) - calculate_timelord_reward(height)
    elif height < period2 * _blocks_per_day:
        return uint64(int(pool_fraction * reward2 * _sten_per_achi)) - calculate_timelord_reward(height)
    elif height < period3 * _blocks_per_day:
        return uint64(int(pool_fraction * reward3 * _sten_per_achi)) - calculate_timelord_reward(height)
    elif height < period4 * _blocks_per_day:
        return uint64(int(pool_fraction * reward4 * _sten_per_achi)) - calculate_timelord_reward(height)
    elif height < period5 * _blocks_per_day:
        return uint64(int(pool_fraction * reward5 * _sten_per_achi)) - calculate_timelord_reward(height)
    elif height < period6 * _blocks_per_day:
        return uint64(int(pool_fraction * reward6 * _sten_per_achi)) - calculate_timelord_reward(height)
    elif height < period7 * _blocks_per_day:
        return uint64(int(pool_fraction * (reward7 * _sten_per_achi - calculate_staker_reward(height)))) - calculate_timelord_reward(height)
    elif height < period8 * _blocks_per_day:
        return uint64(int(pool_fraction * (reward8 * _sten_per_achi - calculate_staker_reward(height)))) - calculate_timelord_reward(height)
    else:
        return uint64(int(pool_fraction * (reward9 * _sten_per_achi - calculate_staker_reward(height)))) - calculate_timelord_reward(height)


def calculate_base_farmer_reward(height: uint32) -> uint64:
    if height == 0:
        return uint64(0)
    elif height < period1 * _blocks_per_day:
        return uint64(int(farmer_fraction * reward1 * _sten_per_achi))
    elif height < period2 * _blocks_per_day:
        return uint64(int(farmer_fraction * reward2 * _sten_per_achi))
    elif height < period3 * _blocks_per_day:
        return uint64(int(farmer_fraction * reward3 * _sten_per_achi))
    elif height < period4 * _blocks_per_day:
        return uint64(int(farmer_fraction * reward4 * _sten_per_achi))
    elif height < period5 * _blocks_per_day:
        return uint64(int(farmer_fraction * reward5 * _sten_per_achi))
    elif height < period6 * _blocks_per_day:
        return uint64(int(farmer_fraction * reward6 * _sten_per_achi))
    elif height < period7 * _blocks_per_day:
        return uint64(int(farmer_fraction * (reward7 * _sten_per_achi - calculate_staker_reward(height))))
    elif height < period8 * _blocks_per_day:
        return uint64(int(farmer_fraction * (reward8 * _sten_per_achi - calculate_staker_reward(height))))
    else:
        return uint64(int(farmer_fraction * (reward9 * _sten_per_achi - calculate_staker_reward(height))))