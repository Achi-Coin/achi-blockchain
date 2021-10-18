from typing import Any

import click


async def convert_async(
    xach_wallet_address,
    ach_wallet_address,
    puzzle_hash,
) -> None:
    import traceback

    from achi.util.bech32m import encode_puzzle_hash
    from achi.util.bech32m import decode_puzzle_hash
    from achi.util.byte_types import hexstr_to_bytes

    try:
        if xach_wallet_address is not None and len(xach_wallet_address) > 0:
            ph = decode_puzzle_hash(xach_wallet_address)
            address = encode_puzzle_hash(ph, "ach")
            print(f"XACH wallet address: {xach_wallet_address}")
            print(f"Puzzle hash: {ph.hex()}")
            print(f"ACH wallet address: {address}")

        if ach_wallet_address is not None and len(ach_wallet_address) > 0:
            ph = decode_puzzle_hash(ach_wallet_address)
            address = encode_puzzle_hash(ph, "xach")
            print(f"ACH wallet address: {ach_wallet_address}")
            print(f"Puzzle hash: {ph.hex()}")
            print(f"XACH wallet address: {address}")

        if puzzle_hash is not None and len(puzzle_hash) > 0:
            ph = hexstr_to_bytes(puzzle_hash)
            xach_address = encode_puzzle_hash(ph, "xach")
            ach_address = encode_puzzle_hash(ph, "ach")
            print(f"Puzzle hash: {ph.hex()}")
            print(f"ACH wallet address: {ach_address}")
            print(f"XACH wallet address: {xach_address}")

    except Exception as e:
        tb = traceback.format_exc()
        print(f"Exception from 'convert' {tb}")


@click.command("convert", short_help="Convert utils")
@click.option(
    "-xa",
    "--xach-wallet-address",
    help=(
        "Set the legacy wallet address (xach). "
    ),
    type=str,
    default=None,
)
@click.option(
    "-a",
    "--ach-wallet-address",
    help=(
        "Set the wallet address (ach). "
    ),
    type=str,
    default=None,
)
@click.option(
    "-p",
    "--puzzle-hash",
    help=(
        "Set the puzzle hash. "
    ),
    type=str,
    default=None,
)

def utils_cmd(
    xach_wallet_address: str,
    ach_wallet_address: str,
    puzzle_hash: str,

) -> None:
    import asyncio

    asyncio.run(
        convert_async(
            xach_wallet_address,
            ach_wallet_address,
            puzzle_hash,
        )
    )
