# coding=utf-8
# standard lib imports
from typing import Union
# project imports
from pyku.channel import Channel
from pyku.roku import Roku


def serialize_roku_object_for_selection(roku: Roku) -> dict:
    return {
        'name': roku.friendly_device_name,
        'value': roku
    }

def merge_roku_config_values_into_dict(config_rokus: list) -> dict:
    return {key: value for config in config_rokus for key, value in config.items()}


def check_if_roku_exists_in_config(roku: Roku, channel: Channel) -> Union[None, dict]:
    config_rokus: Union[list, None] = channel.channel_config.rokus

    if config_rokus is not None and len(config_rokus) > 0:
        for index in range(len(config_rokus)):
            ip_address: Union[str, None] = config_rokus[index][0].get('ip_address', None)
            if ip_address is not None and roku.location.find(ip_address) != -1:
                return merge_roku_config_values_into_dict(config_rokus[index])

    return None
