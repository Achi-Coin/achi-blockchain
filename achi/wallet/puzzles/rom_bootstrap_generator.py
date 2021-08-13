from achi.types.blockchain_format.program import SerializedProgram

from .load_alvm import load_alvm

MOD = SerializedProgram.from_bytes(load_alvm("rom_bootstrap_generator.alvm").as_bin())


def get_generator():
    return MOD
