# Python client and module for Lookyloo Monitoring

There is no public monitoring instance for now, so you will need to
install [your own instance](https://github.com/Lookyloo/monitoring).

## Installation

```bash
pip install pylookyloomonitoring
```

## Usage

### Command line

You can use the `lookyloo_monitor`:

```bash
usage: lookyloo_monitor [-h] --url URL (--monitor_url MONITOR_URL | --compare COMPARE)

Talk to a Lookyloo Monitoring instance.

options:
  -h, --help            show this help message and exit
  --url URL             URL of the instance.
  --monitor_url MONITOR_URL
                        URL to monitor. It will be monitered hourly.
  --compare COMPARE     UUID of the monitoring.
```

### Library

See [API Reference](https://pylookyloomonitoring.readthedocs.io/en/latest/api_reference.html)
