# coding=utf-8
# standard lib imports
import glob
import os
import shutil
from datetime import datetime
from distutils.dir_util import copy_tree
from pathlib import Path
from typing import Union
from zipfile import ZIP_DEFLATED, ZipFile
# third party lib imports
import click
import yaml
# project imports
from pyku.constants import STANDARD_CONFIG, PKKU_CONFIG


class ChannelConfig:
    """
    Channel config class for handling config

    *Attributes:
        file (Path): Path object to the config file in the channel project
        files (list): List of file glob paths to be zipped unpon deployment
        retain_staging_dir (bool): Bool for retaining the zip after deployment
        root (Path): Root path to channel
        out_dir (Path): Path object to the out dir
        rokus (list): List of roku configs
    """
    def __init__(self, config_file: Path):
        with config_file.open('r') as config:
            data: dict = yaml.full_load(config)

        self.file: Path = config_file
        self.files: list = data.get('Files', [])
        self.retain_staging_dir: bool = data.get('RetainStagingDir', False)
        self.root: Path = Path(data.get('Root', ''))
        self.out_dir: Path = Path(data.get('OutDir', ''))
        self.rokus: list = data.get('Rokus', [])
        if not self.out_dir.is_absolute():
            self.out_dir = self.root / self.out_dir


class Channel:
    """
    Channel class for channel management

    *Attributes:
        channel_config (ChannelConfig, None): Channel config read in
        staging_dir (Path, None): Staging dir to be used
        channel_archive (Path, None): Channel archive
        manifest_data (dict, None): Parsed manifest data
        channel_path (Path):
        config_file (Path):
        has_config (bool):

    *methods
        create_config() -> None:

        parse_manifest() -> None:

        stage_channel_for_compilation() -> None:

        archive_staged_content_to_out() -> None:

        empty_dir(dir_to_empty: Path) -> None:
    """
    def __init__(self, channel_path: str):
        self.channel_config: Union[None, ChannelConfig] = None
        self.staging_dir: Union[None, Path] = None
        self.channel_archive: Union[None, Path] = None
        self.manifest_data: Union[None, dict] = None
        self.channel_path: Path = Path(channel_path)
        self.config_file: Path = self.channel_path / PKKU_CONFIG
        self.has_config: bool = False

        if (self.channel_path / PKKU_CONFIG).exists():
            self.has_config = True
            self.channel_config = ChannelConfig(self.config_file)

        if self.channel_config is not None:
            self.parse_manifest()

    def __str__(self) -> str:
        if self.manifest_data is not None:
            required_keys = {'title', 'major_version', 'minor_version', 'build_version'}
            if required_keys <= set(self.manifest_data.keys()):
                return f'{self.manifest_data["title"].replace(" ", "_")}_' \
                       f'{self.manifest_data["major_version"]}.' \
                       f'{self.manifest_data["minor_version"]}.' \
                       f'{self.manifest_data["build_version"]}'

        return f'Channel_{datetime.now()}'

    def create_config(self) -> None:
        """
        Creates pyku config yaml file with default options
        """
        self.config_file.touch(exist_ok=True)
        self.has_config = True
        STANDARD_CONFIG['Root'] = str(self.channel_path)
        STANDARD_CONFIG['OutDir'] = str(self.channel_path / 'out')

        with self.config_file.open('w') as config:
            yaml.dump(STANDARD_CONFIG, config)
            self.channel_config = ChannelConfig(self.config_file)
            self.parse_manifest()

    def parse_manifest(self) -> None:
        """
        Parses channel manifest for data
        """
        if self.channel_config is not None:
            manifest_path: Path = self.channel_config.root / 'manifest'
            manifest_data: dict = {}
            if manifest_path.exists() and manifest_path.is_file():
                with manifest_path.open('r') as manifest:
                    for i, line in enumerate(manifest):
                        if line != '\n':
                            key_pair: list = line.split('=')
                            key, value = key_pair[0], key_pair[1].replace('\n', '')
                            manifest_data = {**manifest_data, **{key: value}}
            self.manifest_data = manifest_data

    def stage_channel_for_compilation(self) -> None:
        """
        Stages channel content in staging dir
        """
        if self.channel_config is not None:
            self.staging_dir = self.channel_config.root / 'staging'
            if not self.staging_dir.exists():
                self.staging_dir.mkdir()

            Channel.empty_dir(self.staging_dir)

            for glob_path in self.channel_config.files:
                full_glob_path: Path = self.channel_config.root / glob_path
                for path in glob.glob(str(full_glob_path)):
                    from_path: Path = Path(path)
                    relative_from: Path = from_path.relative_to(self.channel_config.root)
                    to_path: Path = self.staging_dir / relative_from

                    if from_path.is_file():
                        if not to_path.parent.exists():
                            to_path.parent.mkdir(parents=True)
                        try:
                            shutil.copyfile(str(from_path), str(to_path))
                        except FileNotFoundError:
                            click.echo(f'failed to copy {str(from_path)} into staging')
                    elif from_path.is_dir():
                        copy_tree(str(from_path), str(to_path))

    def archive_staged_content_to_out(self) -> None:
        """
        Creates an archive out of the contents in the staging directory
        """
        if self.channel_config is not None:
            if not self.channel_config.out_dir.exists():
                self.channel_config.out_dir.mkdir(parents=True)

            channel_archive: Path = self.channel_config.out_dir / f'{self.__str__()}'
            os.chdir(str(self.staging_dir))
            shutil.make_archive(
                base_name=str(channel_archive),
                format='zip',
                base_dir='.'
            )

            self.channel_archive = self.channel_config.out_dir / f'{self.__str__()}.zip'

            if self.staging_dir is not None and not self.channel_config.retain_staging_dir:
                Channel.empty_dir(self.staging_dir)
                self.staging_dir.rmdir()

    @staticmethod
    def empty_dir(dir_to_empty: Path) -> None:
        """
        Empties directory of files and child directories
        :param dir_to_empty: Path - path object of directory to be emptied
        :return:
        """
        if dir_to_empty.exists() and dir_to_empty.is_dir():
            for root, dirs, files in os.walk(str(dir_to_empty)):
                for file in files:
                    os.unlink(os.path.join(root, file))
                for directory in dirs:
                    shutil.rmtree(os.path.join(root, directory))
