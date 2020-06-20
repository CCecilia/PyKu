# coding=utf-8
# standard lib imports
import os
import re
from pathlib import Path
from re import Match
from typing import List, Union
# third party lib imports
import requests
from requests.auth import HTTPDigestAuth
from roku_scanner.custom_types import DeviceInfoAttribute, DiscoveryData, Player, RokuApp
from roku_scanner.roku import Roku as RokuDevice
# project imports
from pyku.constants import KEYPRESS_COMMANDS


class Roku(RokuDevice):
    def __init__(self, location: str, discovery_data: DiscoveryData):
        self.advertising_id: DeviceInfoAttribute = None
        self.apps: Union[List[RokuApp], None] = None
        self.build_number: DeviceInfoAttribute = None
        self.can_use_wifi_extender: DeviceInfoAttribute = None
        self.clock_format: DeviceInfoAttribute = None
        self.country: DeviceInfoAttribute = None
        self.data: dict = {}
        self.davinci_version: DeviceInfoAttribute = None
        self.default_device_name: DeviceInfoAttribute = None
        self.developer_enabled: DeviceInfoAttribute = None
        self.device_id: DeviceInfoAttribute = None
        self.discovery_data: DiscoveryData = discovery_data
        self.expert_pq_enabled: DeviceInfoAttribute = None
        self.find_remote_is_possible: DeviceInfoAttribute = None
        self.friendly_device_name: DeviceInfoAttribute = None
        self.friendly_model_name: DeviceInfoAttribute = None
        self.grandcentral_version: DeviceInfoAttribute = None
        self.has_mobile_screensaver: DeviceInfoAttribute = None
        self.has_play_on_roku: DeviceInfoAttribute = None
        self.has_wifi_extender: DeviceInfoAttribute = None
        self.has_wifi_5G_support: DeviceInfoAttribute = None
        self.headphones_connected: DeviceInfoAttribute = None
        self.is_stick: DeviceInfoAttribute = None
        self.is_tv: DeviceInfoAttribute = None
        self.keyed_developer_id: DeviceInfoAttribute = None
        self.language: DeviceInfoAttribute = None
        self.locale: DeviceInfoAttribute = None
        self.location: str = location
        self.model_name: DeviceInfoAttribute = None
        self.model_number: DeviceInfoAttribute = None
        self.model_region: DeviceInfoAttribute = None
        self.notifications_enabled: DeviceInfoAttribute = None
        self.notifications_first_use: DeviceInfoAttribute = None
        self.panel_id: DeviceInfoAttribute = None
        self.password: Union[None, str] = None
        self.player: Union[Player, None] = None
        self.power_mode: DeviceInfoAttribute = None
        self.screen_size: DeviceInfoAttribute = None
        self.search_channels_enabled: DeviceInfoAttribute = None
        self.search_enabled: DeviceInfoAttribute = None
        self.secure_device: DeviceInfoAttribute = None
        self.selected: bool = False
        self.serial_number: DeviceInfoAttribute = None
        self.software_build: DeviceInfoAttribute = None
        self.software_version: DeviceInfoAttribute = None
        self.supports_audio_guide: DeviceInfoAttribute = None
        self.supports_ethernet: DeviceInfoAttribute = None
        self.supports_find_remote: DeviceInfoAttribute = None
        self.supports_private_listening: DeviceInfoAttribute = None
        self.supports_private_listening_dtv: DeviceInfoAttribute = None
        self.supports_rva: DeviceInfoAttribute = None
        self.supports_wake_on_wlan: DeviceInfoAttribute = None
        self.supports_warm_standby: DeviceInfoAttribute = None
        self.supports_suspend: DeviceInfoAttribute = None
        self.support_url: DeviceInfoAttribute = None
        self.time_zone: DeviceInfoAttribute = None
        self.time_zone_auto: DeviceInfoAttribute = None
        self.time_zone_name: DeviceInfoAttribute = None
        self.time_zone_offset: DeviceInfoAttribute = None
        self.time_zone_tz: DeviceInfoAttribute = None
        self.trc_channel_version: DeviceInfoAttribute = None
        self.trc_version: DeviceInfoAttribute = None
        self.tuner_type: DeviceInfoAttribute = None
        self.udn: DeviceInfoAttribute = None
        self.uptime: DeviceInfoAttribute = None
        self.user_device_name: DeviceInfoAttribute = None
        self.user_device_location: DeviceInfoAttribute = None
        self.user_name: str = 'rokudev'
        self.vendor_name: DeviceInfoAttribute = None
        self.voice_search_enabled: DeviceInfoAttribute = None
        self.wifi_driver: DeviceInfoAttribute = None
        self.wifi_mac: DeviceInfoAttribute = None

    def get_ip_address(self):
        return self.location.split(':')[1][2:]

    def send_remote_command(self, command: str) -> None:
        allowed_commands: list = KEYPRESS_COMMANDS

        if self.find_remote_is_possible:
            allowed_commands.append('findremote')

        if self.is_tv:
            allowed_commands.append([
                'volumedown',
                'volumemute',
                'volumeup',
                'poweroff',
                'channelup',
                'channeldown',
                'inputtuner',
                'inputhdmi1',
                'inputhdmi2',
                'inputhdmi3',
                'inputhdmi4',
                'inputav1'
            ])

        if command.lower() not in allowed_commands:
            raise Exception('unknown command')

        requests.post(f'{self.location}keypress/{command}')

    @staticmethod
    def parse_plugin_installer_output(output_html: str) -> list:
        messages: list = re.findall(r'Shell\.create\(.+\)\.trigger\(.+\)\.trigger\(.+\)', output_html)
        temp: list = []
        for message in messages:
            status_message_match: Match = re.search(r'.\(\'Set message type\',.+?\)', message)
            status_message: str = message[status_message_match.start(): status_message_match.end()]
            status_message_arr: list = re.split(',', status_message)
            status: str = re.sub(r'[^A-Za-z0-9]+', '', status_message_arr[1])

            message_content_match: Match = re.search(r'.\(\'Set message content\',.+?\)', message)
            message_content: str = message[message_content_match.start(): message_content_match.end()]
            message_content_arr: list = re.split(',', message_content)
            content_message: str = re.sub(r'[^A-Za-z0-9]+', '', message_content_arr[1])

            temp.append({
                'status': status,
                'msg': content_message
            })

        return temp

    def delete_dev_app(self):
        self.send_remote_command('home')
        # TODO: solve auth digest issue with using requests module
        # res = requests.post(
        #     url=f'http://{self.get_ip_address()}/plugin_install',
        #     auth=HTTPDigestAuth(self.user_name, self.password),
        #     data=[
        #         ('mysubmit', 'Delete'),
        #         ('archive', '')
        #     ],
        #     verify=False,
        #     stream=True,
        #     timeout=10
        # )
        delete_cmd: str = f'curl --user {self.user_name}:{str(self.password)} --digest -s -S ' \
                          f'-F "mysubmit=Delete" ' \
                          f'-F "archive=''"  ' \
                          f'http://{self.get_ip_address()}/plugin_install'
        results: str = os.popen(delete_cmd).read()
        messages: list = Roku.parse_plugin_installer_output(results)
        if len(messages) > 0:
            return messages

        return [{'status': 'error', 'msg': 'command failed'}]

    def deploy_archive(self, channel_archive: Path):
        self.send_remote_command('home')
        self.delete_dev_app()
        deploy_cmd: str = f'curl --user {self.user_name}:{str(self.password)} --digest -s -S ' \
                          f'-F "mysubmit=Replace" ' \
                          f'-F "archive=@{str(channel_archive)}"  ' \
                          f'http://{self.get_ip_address()}/plugin_install'
        results = os.popen(deploy_cmd).read()
        messages: list = Roku.parse_plugin_installer_output(results)
        if len(messages) > 0:
            return messages

        return [{'status': 'error', 'msg': 'command failed'}]



