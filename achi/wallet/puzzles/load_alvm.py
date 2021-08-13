import pathlib

import pkg_resources
from alvm_tools.alvmc import compile_alvm

from achi.types.blockchain_format.program import Program, SerializedProgram


def load_serialized_alvm(alvm_filename, package_or_requirement=__name__) -> SerializedProgram:
    """
    This function takes a .alvm file in the given package and compiles it to a
    .alvm.hex file if the .hex file is missing or older than the .alvm file, then
    returns the contents of the .hex file as a `Program`.

    alvm_filename: file name
    package_or_requirement: usually `__name__` if the alvm file is in the same package
    """

    hex_filename = f"{alvm_filename}.hex"

    try:
        if pkg_resources.resource_exists(package_or_requirement, alvm_filename):
            full_path = pathlib.Path(pkg_resources.resource_filename(package_or_requirement, alvm_filename))
            output = full_path.parent / hex_filename
            compile_alvm(full_path, output, search_paths=[full_path.parent])
    except NotImplementedError:
        # pyinstaller doesn't support `pkg_resources.resource_exists`
        # so we just fall through to loading the hex alvm
        pass

    alvm_hex = pkg_resources.resource_string(package_or_requirement, hex_filename).decode("utf8")
    alvm_blob = bytes.fromhex(alvm_hex)
    return SerializedProgram.from_bytes(alvm_blob)


def load_alvm(alvm_filename, package_or_requirement=__name__) -> Program:
    return Program.from_bytes(bytes(load_serialized_alvm(alvm_filename, package_or_requirement=__name__)))
