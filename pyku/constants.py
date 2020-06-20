# coding=utf-8
STANDARD_CONFIG: dict = {
    'Root': '',
    'Files': [
        'manifest',
        'components/**/*',
        'source/**/*',
        'images/**/*'
    ],
    'OutDir': '',
    'RetainStagingDir': False
}
PKKU_CONFIG = 'pyku_config.yml'
KEYPRESS_COMMANDS: list = [
    'home',
    'rev',
    'fwd',
    'play',
    'select',
    'left',
    'right',
    'down',
    'up',
    'back',
    'instantreplay',
    'info',
    'backspace',
    'search',
    'enter'
]
