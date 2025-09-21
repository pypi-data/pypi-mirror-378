# pyvkpns

![RuStore Logo](https://upload.wikimedia.org/wikipedia/commons/e/e5/RuStore_logo.svg)

Python client for push notifications in RuStore.

## Features

- Send and receive push notifications
- Easy integration with Python projects
- Works with RuStore notification service

## Installation

Install via pip:

```bash
pip install pyvkpns
```
Or from source:

```bash
git clone https://github.com/deadlovelll/pyvkpns.git
cd pyvkpns
pip install .
```

## Usage

```py
from pyvkpns import VKPNSClient

client = VKPNSClient(
    project_id="YOUR_PROJECT_ID", 
    service_token="YOUR_SERVICE_TOKEN",
    platform="PLATFORM",
)
await client.send_notification(
    title="Hello", 
    body="This is a test notification",
)
```

## Contributing

Contributions are welcome. Please open issues or submit pull requests.

License
MIT License © 2025 Timofei Ivankov