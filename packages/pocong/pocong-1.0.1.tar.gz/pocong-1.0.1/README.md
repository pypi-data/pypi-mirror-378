<p align="center">
  <img src="https://i.ibb.co.com/35P4Nq9x/Screenshot-2025-08-22-at-18-40-11.png?width=128" alt="POCONG Logo" width="128"/>
</p>

# POCONG 🪦
**Python Oriented Crawling ON Going**

POCONG is a lightweight web crawling framework built in Python.

## Installation
```bash
pip install pocong
```

## Usage: Get Proxy from proxy_spiders

You can use the `get_proxy` and `get_proxy_random` methods from `proxy_spiders` to fetch working proxies.

```python
from pocong.proxy_spiders import GetProxy

gp = GetProxy()

# Get the first working proxy
proxy = gp.get_proxy()
print("First working proxy:", proxy)
```
```python
from pocong.proxy_spiders import GetProxy

gp = GetProxy()

# Get a random working proxy
random_proxy = gp.get_proxy_random()
print("Random working proxy:", random_proxy)
```

Sample output:
```
First working proxy: {'ip': '123.45.67.89', 'port': '8080', 'https': 'yes', ...}
Random working proxy: {'ip': '98.76.54.32', 'port': '3128', 'https': 'yes', ...}
```

You can use the returned proxy dictionary with the `requests` library, for example:

```python
import requests

proxy = gp.get_proxy()
if proxy:
    proxies = {
        'http': f"http://{proxy['ip']}:{proxy['port']}",
        'https': f"http://{proxy['ip']}:{proxy['port']}"
    }
    response = requests.get('https://httpbin.org/ip', proxies=proxies)
    print(response.json())
else:
    print("No working proxy found.")
```

- `get_proxy()` will return the first working proxy found.
- `get_proxy_random()` will return a random working proxy (with up to 20 retries).

Both methods return a dictionary with proxy details (e.g., `{ 'ip': '...', 'port': '...', ... }`) or `None` if no working proxy is found.
