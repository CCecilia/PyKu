# PyKu 1.0.0

CLI for aiding in Roku/Brightscript channel development.

### Prerequisites
* [Python3.8+](https://www.python.org/downloads/)
* PIP - should be installed with python, if not [here](https://pip.pypa.io/en/stable/installing/)

## Installation
```shell script
pip3 install pyku
```

## Usage

### CLI
```shell script
python3 -m pyku
```

#### Options
Deploying a dev channel.
```shell script
python3 -m pyku deploy -c {{path_to_channel}}
```

## Testing

```shell script
pytest tests/
```

## Code Standard
PyKu follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) standard.

## Versioning

PyKu uses [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/CCecilia/PyKu/tags).

## Authors

* **Christian Cecilia** - *Initial work*

See also the list of [contributors](https://github.com/CCecilia/PyKu/graphs/contributors) who participated in this project.

## Thanks

[Roku Dev](https://github.com/rokudev) for test channel assets. Also this is great place for code samples to learn from.