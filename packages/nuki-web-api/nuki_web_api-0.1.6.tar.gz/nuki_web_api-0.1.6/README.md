# nuki-web-api

A Python wrapper for the [Nuki Web API](https://api.nuki.io/).

## Installation

```bash
pip install nuki-web-api
```


## Usage
```Python
from nukiwebapi import NukiWebAPI

client = NukiWebAPI("YOUR_ACCESS_TOKEN")

for lock_id, lock in client.lock_instances:
    print(lock.name)
    print(lock.hex_id)

    print(lock.is_locked)
    print(lock.battery_charge)

```

## Disclaimer

This API wrapper is in **Alpha** stage. I do not have the resources to fully test all provided methods against the API (e.g. account deletion).
The methods provided by the API can potentially mess with devices directly linked to your personal safety (i.e. your home!).

**Use with caution.**

