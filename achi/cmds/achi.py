import click

from achi import __version__
from achi.cmds.configure import configure_cmd
from achi.cmds.farm import farm_cmd
from achi.cmds.init import init_cmd
from achi.cmds.keys import keys_cmd
from achi.cmds.netspace import netspace_cmd
from achi.cmds.plots import plots_cmd
from achi.cmds.show import show_cmd
from achi.cmds.start import start_cmd
from achi.cmds.stop import stop_cmd
from achi.cmds.wallet import wallet_cmd
from achi.cmds.utils import utils_cmd
from achi.util.default_root import DEFAULT_ROOT_PATH

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def monkey_patch_click() -> None:
    # this hacks around what seems to be an incompatibility between the python from `pyinstaller`
    # and `click`
    #
    # Not 100% sure on the details, but it seems that `click` performs a check on start-up
    # that `codecs.lookup(locale.getpreferredencoding()).name != 'ascii'`, and refuses to start
    # if it's not. The python that comes with `pyinstaller` fails this check.
    #
    # This will probably cause problems with the command-line tools that use parameters that
    # are not strict ascii. The real fix is likely with the `pyinstaller` python.

    import click.core

    click.core._verify_python3_env = lambda *args, **kwargs: 0  # type: ignore


@click.group(
    help=f"\n  Manage achi blockchain infrastructure ({__version__})\n",
    epilog="Try 'achi start node', 'achi netspace -d 192', or 'achi show -s'",
    context_settings=CONTEXT_SETTINGS,
)
@click.option("--root-path", default=DEFAULT_ROOT_PATH, help="Config file root", type=click.Path(), show_default=True)
@click.pass_context
def cli(ctx: click.Context, root_path: str) -> None:
    from pathlib import Path

    ctx.ensure_object(dict)
    ctx.obj["root_path"] = Path(root_path)


@cli.command("version", short_help="Show achi version")
def version_cmd() -> None:
    print(__version__)


@cli.command("run_daemon", short_help="Runs achi daemon")
@click.pass_context
def run_daemon_cmd(ctx: click.Context) -> None:
    from achi.daemon.server import async_run_daemon
    import asyncio

    asyncio.get_event_loop().run_until_complete(async_run_daemon(ctx.obj["root_path"]))


cli.add_command(keys_cmd)
cli.add_command(plots_cmd)
cli.add_command(wallet_cmd)
cli.add_command(configure_cmd)
cli.add_command(init_cmd)
cli.add_command(show_cmd)
cli.add_command(start_cmd)
cli.add_command(stop_cmd)
cli.add_command(netspace_cmd)
cli.add_command(farm_cmd)
cli.add_command(utils_cmd)


def main() -> None:
    monkey_patch_click()
    cli()  # pylint: disable=no-value-for-parameter


if __name__ == "__main__":
    main()
