from pathlib import Path
from unittest import TestCase

from alvm_tools.alvmc import compile_alvm

from achi.types.blockchain_format.program import Program, SerializedProgram

wallet_program_files = set(
    [
        "achi/wallet/puzzles/calculate_synthetic_public_key.alvm",
        "achi/wallet/puzzles/cc.alvm",
        "achi/wallet/puzzles/achilang_deserialisation.alvm",
        "achi/wallet/puzzles/rom_bootstrap_generator.alvm",
        "achi/wallet/puzzles/generator_for_single_coin.alvm",
        "achi/wallet/puzzles/genesis-by-coin-id-with-0.alvm",
        "achi/wallet/puzzles/genesis-by-puzzle-hash-with-0.alvm",
        "achi/wallet/puzzles/lock.inner.puzzle.alvm",
        "achi/wallet/puzzles/p2_conditions.alvm",
        "achi/wallet/puzzles/p2_delegated_conditions.alvm",
        "achi/wallet/puzzles/p2_delegated_puzzle.alvm",
        "achi/wallet/puzzles/p2_delegated_puzzle_or_hidden_puzzle.alvm",
        "achi/wallet/puzzles/p2_m_of_n_delegate_direct.alvm",
        "achi/wallet/puzzles/p2_puzzle_hash.alvm",
        "achi/wallet/puzzles/rl_aggregation.alvm",
        "achi/wallet/puzzles/rl.alvm",
        "achi/wallet/puzzles/sha256tree_module.alvm",
        "achi/wallet/puzzles/singleton_top_layer.alvm",
        "achi/wallet/puzzles/did_innerpuz.alvm",
        "achi/wallet/puzzles/decompress_puzzle.alvm",
        "achi/wallet/puzzles/decompress_coin_solution_entry_with_prefix.alvm",
        "achi/wallet/puzzles/decompress_coin_solution_entry.alvm",
        "achi/wallet/puzzles/block_program_zero.alvm",
        "achi/wallet/puzzles/test_generator_deserialize.alvm",
        "achi/wallet/puzzles/test_multiple_generator_input_arguments.alvm",
    ]
)

alvm_include_files = set(
    ["achi/wallet/puzzles/create-lock-puzzlehash.alvm", "achi/wallet/puzzles/condition_codes.alvm"]
)

ALVM_PROGRAM_ROOT = "achi/wallet/puzzles"


def list_files(dir, glob):
    dir = Path(dir)
    entries = dir.glob(glob)
    files = [f for f in entries if f.is_file()]
    return files


def read_file(path):
    with open(path) as f:
        return f.read()


def path_with_ext(path, ext):
    return Path(str(path) + ext)


class TestAlvmCompilation(TestCase):
    """
    These are tests, and not just build scripts to regenerate the bytecode, because
    the developer must be aware if the compiled output changes, for any reason.
    """

    def test_all_programs_listed(self):
        """
        Checks to see if a new .alvm file was added to achi/wallet/puzzles, but not added to `wallet_program_files`
        """
        existing_files = list_files(ALVM_PROGRAM_ROOT, "*.alvm")
        existing_file_paths = set([Path(x).relative_to(ALVM_PROGRAM_ROOT) for x in existing_files])

        expected_files = set(alvm_include_files).union(set(wallet_program_files))
        expected_file_paths = set([Path(x).relative_to(ALVM_PROGRAM_ROOT) for x in expected_files])

        self.assertEqual(
            expected_file_paths,
            existing_file_paths,
            msg="Please add your new program to `wallet_program_files` or `alvm_include_files.values`",
        )

    def test_include_and_source_files_separate(self):
        self.assertEqual(alvm_include_files.intersection(wallet_program_files), set())

    # TODO: Test recompilation with all available compiler configurations & implementations
    def test_all_programs_are_compiled(self):
        """Checks to see if a new .alvm file was added without its .hex file"""
        all_compiled = True
        msg = "Please compile your program with:\n"

        # Note that we cannot test all existing .alvm files - some are not
        # meant to be run as a "module" with load_alvm; some are include files
        # We test for inclusion in `test_all_programs_listed`
        for prog_path in wallet_program_files:
            try:
                output_path = path_with_ext(prog_path, ".hex")
                hex = output_path.read_text()
                self.assertTrue(len(hex) > 0)
            except Exception as ex:
                all_compiled = False
                msg += f"    run -i {prog_path.parent} -d {prog_path} > {prog_path}.hex\n"
                print(ex)
        msg += "and check it in"
        self.assertTrue(all_compiled, msg=msg)

    def test_recompilation_matches(self):
        self.maxDiff = None
        for f in wallet_program_files:
            f = Path(f)
            compile_alvm(f, path_with_ext(f, ".recompiled"), search_paths=[f.parent])
            orig_hex = path_with_ext(f, ".hex").read_text().strip()
            new_hex = path_with_ext(f, ".recompiled").read_text().strip()
            self.assertEqual(orig_hex, new_hex, msg=f"Compilation of {f} does not match {f}.hex")
        pass

    def test_all_compiled_programs_are_hashed(self):
        """Checks to see if a .hex file is missing its .sha256tree file"""
        all_hashed = True
        msg = "Please hash your program with:\n"
        for prog_path in wallet_program_files:
            try:
                hex = path_with_ext(prog_path, ".hex.sha256tree").read_text()
                self.assertTrue(len(hex) > 0)
            except Exception as ex:
                print(ex)
                all_hashed = False
                msg += f"    opd -H {prog_path}.hex | head -1 > {prog_path}.hex.sha256tree\n"
        msg += "and check it in"
        self.assertTrue(all_hashed, msg)

    # TODO: Test all available shatree implementations on all progams
    def test_shatrees_match(self):
        """Checks to see that all .sha256tree files match their .hex files"""
        for prog_path in wallet_program_files:
            # load the .hex file as a program
            hex_filename = path_with_ext(prog_path, ".hex")
            alvm_hex = hex_filename.read_text()  # .decode("utf8")
            alvm_blob = bytes.fromhex(alvm_hex)
            s = SerializedProgram.from_bytes(alvm_blob)
            p = Program.from_bytes(alvm_blob)

            # load the checked-in shatree
            existing_sha = path_with_ext(prog_path, ".hex.sha256tree").read_text().strip()

            self.assertEqual(
                s.get_tree_hash().hex(),
                existing_sha,
                msg=f"Checked-in shatree hash file does not match shatree hash of loaded SerializedProgram: {prog_path}",  # noqa
            )
            self.assertEqual(
                p.get_tree_hash().hex(),
                existing_sha,
                msg=f"Checked-in shatree hash file does not match shatree hash of loaded Program: {prog_path}",
            )
