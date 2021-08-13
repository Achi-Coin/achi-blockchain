from unittest import TestCase

from achi.types.blockchain_format.program import Program, SerializedProgram, INFINITE_COST
from achi.wallet.puzzles.load_alvm import load_alvm

SHA256TREE_MOD = load_alvm("sha256tree_module.alvm")


# TODO: test multiple args
class TestSerializedProgram(TestCase):
    def test_tree_hash(self):
        p = SHA256TREE_MOD
        s = SerializedProgram.from_bytes(bytes(SHA256TREE_MOD))
        self.assertEqual(s.get_tree_hash(), p.get_tree_hash())

    def test_program_execution(self):
        p_result = SHA256TREE_MOD.run(SHA256TREE_MOD)
        sp = SerializedProgram.from_bytes(bytes(SHA256TREE_MOD))
        cost, sp_result = sp.run_with_cost(INFINITE_COST, sp)
        self.assertEqual(p_result, sp_result)

    def test_serialization(self):
        s0 = SerializedProgram.from_bytes(b"\x00")
        p0 = Program.from_bytes(b"\x00")
        print(s0, p0)
        # TODO: enable when alvm updated for minimal encoding of zero
        # self.assertEqual(bytes(p0), bytes(s0))
