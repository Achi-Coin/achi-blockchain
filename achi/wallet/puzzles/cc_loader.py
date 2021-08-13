from achi.wallet.puzzles.load_alvm import load_alvm

CC_MOD = load_alvm("cc.alvm", package_or_requirement=__name__)
LOCK_INNER_PUZZLE = load_alvm("lock.inner.puzzle.alvm", package_or_requirement=__name__)
