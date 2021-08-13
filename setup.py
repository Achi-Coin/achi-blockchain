from setuptools import setup

dependencies = [
    "blspy==1.0.2",  # Signature library
    "achivdf==1.0.1",  # timelord and vdf verification
    "achibip158==1.0",  # bip158-style wallet filters
    "achipos==1.0.2",  # proof of space
    "alvm==0.9.6",
    "alvm_rs==0.1.7",
    "alvm_tools==0.4.3",
    "aiohttp==3.7.4",  # HTTP server for full node rpc
    "aiosqlite==0.17.0",  # asyncio wrapper for sqlite, to store blocks
    "bitstring==3.1.7",  # Binary data management library
    "colorlog==5.0.1",  # Adds color to logs
    "concurrent-log-handler==0.9.19",  # Concurrently log and rotate logs
    "cryptography==3.4.7",  # Python cryptography library for TLS - keyring conflict
    "keyring==23.0.1",  # Store keys in MacOS Keychain, Windows Credential Locker
    "keyrings.cryptfile==1.3.4",  # Secure storage for keys on Linux (Will be replaced)
    #  "keyrings.cryptfile==1.3.8",  # Secure storage for keys on Linux (Will be replaced)
    #  See https://github.com/frispete/keyrings.cryptfile/issues/15
    "PyYAML==5.4.1",  # Used for config file format
    "setproctitle==1.2.2",  # Gives the achi processes readable names
    "sortedcontainers==2.3.0",  # For maintaining sorted mempools
    "websockets==8.1.0",  # For use in wallet RPC and electron UI
    "click==7.1.2",  # For the CLI
    "dnspython==2.1.0",  # Query DNS seeds
]

upnp_dependencies = [
    "miniupnpc==2.1",  # Allows users to open ports on their router
]

dev_dependencies = [
    "pytest",
    "pytest-asyncio",
    "flake8",
    "mypy",
    "black",
    "aiohttp_cors",  # For blackd
    "ipython",  # For asyncio debugging
]

kwargs = dict(
    name="achi-blockchain",
    author="Sten Achiho",
    author_email="sten@achicoin.org",
    description="Achi blockchain full node, farmer, timelord, and wallet.",
    url="https://achicoin.org/",
    license="Apache License",
    python_requires=">=3.7, <4",
    keywords="achi blockchain node",
    install_requires=dependencies,
    #setup_requires=["setuptools_scm"],
    extras_require=dict(
        uvloop=["uvloop"],
        dev=dev_dependencies,
        upnp=upnp_dependencies,
    ),
    packages=[
        "achi",
        "achi.cmds",
        "achi.consensus",
        "achi.daemon",
        "achi.full_node",
        "achi.timelord",
        "achi.farmer",
        "achi.harvester",
        "achi.introducer",
        "achi.plotting",
        "achi.protocols",
        "achi.rpc",
        "achi.server",
        "achi.simulator",
        "achi.types.blockchain_format",
        "achi.types",
        "achi.util",
        "achi.wallet",
        "achi.wallet.puzzles",
        "achi.wallet.rl_wallet",
        "achi.wallet.cc_wallet",
        "achi.wallet.did_wallet",
        "achi.wallet.settings",
        "achi.wallet.trading",
        "achi.wallet.util",
        "achi.ssl",
        "mozilla-ca",
    ],
    entry_points={
        "console_scripts": [
            "achi = achi.cmds.achi:main",
            "achi_wallet = achi.server.start_wallet:main",
            "achi_full_node = achi.server.start_full_node:main",
            "achi_harvester = achi.server.start_harvester:main",
            "achi_farmer = achi.server.start_farmer:main",
            "achi_introducer = achi.server.start_introducer:main",
            "achi_timelord = achi.server.start_timelord:main",
            "achi_timelord_launcher = achi.timelord.timelord_launcher:main",
            "achi_full_node_simulator = achi.simulator.start_simulator:main",
        ]
    },
    package_data={
        "achi": ["pyinstaller.spec"],
        "achi.wallet.puzzles": ["*.alvm", "*.alvm.hex"],
        "achi.util": ["initial-*.yaml", "english.txt"],
        "achi.ssl": ["achi_ca.crt", "achi_ca.key", "dst_root_ca.pem"],
        "mozilla-ca": ["cacert.pem"],
    },
    #use_scm_version={"fallback_version": "unknown-no-.git-directory"},
    version="1.1.6",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    zip_safe=False,
)


if __name__ == "__main__":
    setup(**kwargs)
