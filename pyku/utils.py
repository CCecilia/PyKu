# coding=utf-8
"""
Usage:
    Utility functions to help with PyKu commmands

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


def serialize_roku_object_for_selection(roku: Roku) -> dict:
    """
    Serailizes Roku into a usable dict to prompt.
    :param roku: Roku device
    :return: choice dict for prompt
    """
    return {
        'name': roku.friendly_device_name,
        'value': roku
    }


def merge_roku_config_values_into_dict(config_rokus: list) -> dict:
    """
    Merges the list dicts and values from config into one dict for ease of access
    :param config_rokus: list of roku cofig value dict
    :return: a single dict of config values
    """
    return {key: value for config in config_rokus for key, value in config.items()}


def check_if_roku_exists_in_config(roku: Roku, channel: Channel) -> Union[None, dict]:
    """
    Checks if a Roku's ip address exists in the config and returns amerged version of it if True else None
    :param roku: Roku device
    :param channel: Channel
    :return:
    """
    config_rokus: Union[list, None] = channel.channel_config.rokus

    if config_rokus is not None and len(config_rokus) > 0:
        for index in range(len(config_rokus)):
            ip_address: Union[str, None] = config_rokus[index][0].get('ip_address', None)
            if ip_address is not None and roku.location.find(ip_address) != -1:
                return merge_roku_config_values_into_dict(config_rokus[index])

    return None


def run_device_discovery(channel: Channel) -> list:
    """
    Discovers devices on LAN and cross references config for password or prompts user for it
    :param channel: Channel
    :return: list of selected devices
    """
    # Discover devices
    click.echo('discovering devices')
    scanner: Scanner = Scanner()
    scanner.discover()
    selected_devices: list = []
    rokus: list = []

    for device in scanner.discovered_devices:
        roku_location: str = device.get('LOCATION')
        roku: Roku = Roku(location=roku_location, discovery_data=device)
        roku.fetch_data()
        rokus.append(roku)

    if len(rokus) > 0:
        # setup rokus for selection prompt
        choices: list = [serialize_roku_object_for_selection(roku) for roku in rokus if roku.developer_enabled]
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
                config_check: Union[None, dict] = check_if_roku_exists_in_config(selected, channel)
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

    return selected_devices


def get_selected_from_config(channel: Channel):
    """
    Reads config for devices and creates Roku objects
    :param channel: Channel
    :return: list of selected devices
    """
    # create roku objects from config
    click.echo('reading config for rokus')
    selected_devices: list = []
    config_rokus: list = channel.channel_config.rokus
    if not len(config_rokus):
        click.echo('cannot skip device discovery without rokus designated in config')

    for roku_config in config_rokus:
        roku_config = merge_roku_config_values_into_dict(roku_config)
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

    return selected_devices
