# logsteplib

* [Description](#package-description)
* [Usage](#usage)
* [Installation](#installation)
* [License](#license)

## Package Description

Package containing a standard format for the logging module.

## Usage

* [logsteplib](#logsteplib)

from a script:

```python
import logsteplib

process_name = "XPTO"
logger = logsteplib.get_logger(name=process_name)
```

## Installation

* [logsteplib](#logsteplib)

Install python and pip if you have not already.

Then run:

```bash
pip install pip --upgrade
```

For production:

```bash
pip install logsteplib
```

This will install the package and all of it's python dependencies.

If you want to install the project for development:

```bash
git clone https://github.com/aghuttun/logsteplib.git
cd logsteplib
pip install -e ".[dev]"
```

To test the development package: [Testing](#testing)

## License

* [logsteplib](#logsteplib)

BSD License (see license file)
