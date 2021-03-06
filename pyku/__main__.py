# coding=utf-8
"""
Usage:
    python3 -m pyku

Commands:
    deploy - create and deploys a channel archive to Roku(s)

    Flags:
        -c, --channel - Path to channel to be deployed, REQUIRED
        --skip-discovery - skip device discovery and use only device designated in config

    keypress - simulates a remote keypress

    Flags:
        -b, --button - Button pressed, REQUIRED
        -c, --channel - Path to channel to be deployed, REQUIRED
        --skip-discovery - skip device discovery and use only device designated in config
ToDos:
"""
# standard lib imports
from typing import Union
# third party lib imports
import click
# project imports
from pyku.channel import Channel
from pyku.roku import Roku
import pyku.utils as utils


@click.group()
def cli():
    """
    Intermediatory function for click to routes commands
    :return:
    """
    pass


@cli.command()
@click.option(
    '-c',
    '--channel',
    'channel_path',
    help='Path to channel project\'s root dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=False, readable=True),
    required=True
)
@click.option('--skip-discovery', 'skip_discovery', flag_value=True)
@click.option('--debugger', 'debugger', flag_value=True)
def deploy(channel_path: str, skip_discovery: bool, debugger: bool):
    """
    Deploy Command
    :param channel_path: Path to channel project's root dir
    :param skip_discovery: falg to skip device discovery and use config rokus
    """
    click.echo('deploy')
    channel: Channel = Channel(channel_path)
    # Checking for channel config
    if not channel.has_config:
        create_config = click.confirm(
            'Config missing, create pyku_config.yml',
            default=True,
            abort=True
        )
        if create_config:
            channel.create_config()
            click.echo(f'created config {str(channel.config_file)}')
            click.confirm(
                'Continue with default config',
                default=True,
                abort=True,
                prompt_suffix='?'
            )

    # Create channel archive
    click.echo('staging channel')
    channel.stage_channel_for_compilation()
    click.echo('creating archive')
    channel.archive_staged_content_to_out()
    selected_devices: list = []
    deploy_status: str = "false"

    if not skip_discovery:
        selected_devices = utils.run_device_discovery(channel)
    else:
        selected_devices = utils.get_selected_from_config(channel)

    # loop through selected rokus and deploy archives
    if len(selected_devices) > 0:
        for selected in selected_devices:
            result_msgs: list = selected.deploy_archive(channel.channel_archive)
            for msg in result_msgs:
                deploy_status = msg["status"]
                click.echo(f'{selected.friendly_model_name} | Status {deploy_status} | {msg["msg"]}')

    if deploy_status == "success" and debugger:
        print("run debugger")


@cli.command()
@click.option(
    '-b',
    '--button',
    help='Simulated button pressed',
    type=str,
    required=True
)
@click.option(
    '-c',
    '--channel',
    'channel_path',
    help='Path to channel project\'s root dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=False, readable=True),
    required=False
)
@click.option('--skip-discovery', 'skip_discovery', flag_value=True)
def keypress(button: str, channel_path: str, skip_discovery: bool):
    click.echo('key press')
    channel: Channel = Channel(channel_path)
    selected_devices: list = []

    if not skip_discovery:
        selected_devices.append(utils.run_device_discovery(channel))
    else:
        selected_devices.append(utils.get_selected_from_config(channel))

    if len(selected_devices) > 0:
        for selected in selected_devices:
            selected.send_remote_command(button)


if __name__ == '__main__':
    cli()
