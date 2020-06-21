# coding=utf-8
"""
Usage:
    python3 -m pyku

Commands:
    deploy - create and deploys a channel archive to Roku(s)

    Flags:
        -c, --channel - Path to channel to be deployed, REQUIRED
        --skip-discovery - skip device discovery and use only device designated in config
ToDos:
"""
# standard lib imports
from typing import Union
# third party lib imports
import click
from PyInquirer import prompt
from roku_scanner.scanner import Scanner
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
def deploy(channel_path: str, skip_discovery: bool):
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
    rokus: list = []
    selected_devices: list = []

    if not skip_discovery:
        # Discover devices
        click.echo('discovering devices')
        scanner: Scanner = Scanner()
        scanner.discover()

        for device in scanner.discovered_devices:
            roku_location: str = device.get('LOCATION')
            roku: Roku = Roku(location=roku_location, discovery_data=device)
            roku.fetch_data()
            rokus.append(roku)

        if len(rokus) > 0:
            # setup rokus for selection prompt
            choices: list = [utils.serialize_roku_object_for_selection(roku) for roku in rokus if roku.developer_enabled]
            device_selection_questions: list = [
                {
                    "type": 'checkbox',
                    "message": 'Select Device(s)',
                    "name": 'selected_devices',
                    "choices": choices,
                    'validate': lambda answer: 'You must choose at least one device.'
                    if len(answer) == 0 else True
                }
            ]
            selected_rokus: dict = prompt(device_selection_questions)
            selected_devices.append(selected_rokus.get('selected_devices', []))

            if len(selected_devices) > 0:
                # check for roku dev password in config or prompt user for it
                for selected in selected_devices:
                    config_check: Union[None, dict] = utils.check_if_roku_exists_in_config(selected, channel)
                    if config_check is not None:
                        selected.password = config_check.get('password', None)
                        selected.selected = True
                        config_username: Union[str, None] = config_check.get('username', None)
                        if config_username is not None:
                            selected.user_name = config_username
                    else:
                        password_prompt: str = click.prompt(
                            f'password for {selected.location}',
                            prompt_suffix='? ',
                            type=str
                        )
                        if password_prompt != '':
                            selected.password = password_prompt
                            selected.selected = True
                        else:
                            selected_devices.remove(selected)
                            click.echo(f'unable to use {selected.friendly_model_name} @ {selected.location}')

                    selected.deploy_archive(channel.channel_archive)
    else:
        # create roku objects from config
        click.echo('reading config for rokus')
        config_rokus: list = channel.channel_config.rokus
        if not len(config_rokus):
            click.echo('cannot skip device discovery without rokus designated in config')

        for roku_config in config_rokus:
            roku_config = utils.merge_roku_config_values_into_dict(roku_config)
            click.echo(f'found config for {roku_config.get("ip_address", "")}')
            roku: Roku = Roku(
                location=f'http://{roku_config.get("ip_address", "")}:8060/',
                discovery_data={
                    'WAKEUP': '',
                    'device-group.roku.com': '',
                    'LOCATION': f'http://{roku_config.get("ip_address", "")}:8060/',
                    'Server': 'Roku/9.3.0 UPnP/1.0 Roku/9.3.0',
                    'Ext': '',
                    'USN': '',
                    'ST': 'roku:ecp',
                    'Cache-Control': 'max-age=3600'
                }
            )
            roku.fetch_data()
            roku.selected = True
            roku.password = roku_config.get("password", "")
            config_username: Union[str, None] = roku_config.get('username', None)
            if config_username is not None:
                roku.user_name = config_username
            selected_devices.append(roku)

    # loop through selected rokus and deploy archives
    if len(selected_devices) > 0:
        for selected in selected_devices:
            result_msgs: list = selected.deploy_archive(channel.channel_archive)
            for msg in result_msgs:
                click.echo(f'{selected.friendly_model_name} | Status {msg["status"]} | {msg["msg"]}')


if __name__ == '__main__':
    cli()
