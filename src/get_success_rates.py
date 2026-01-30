import requests
import asyncio
import aiohttp
import pandas as pd


MAX_CONCURRENT=200

endpoints = [  
    "https://api.ipify.org?format=json",
    "https://ifconfig.me/ip",
    "https://checkip.amazonaws.com",
    "https://httpbin.org/get",
    "https://postman-echo.com/get",
    "https://www.google.com",
    "https://www.cloudflare.com",
]

def get_raw_proxy_ips():
    proxy_list = requests.get('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt')
    return proxy_list.text.split()

async def test_proxy(i, proxy_ip, endpoints, session, semaphore):
    num_successes = 0
    proxy_url = f'http://{proxy_ip}'

    async def fetch(url):
        nonlocal num_successes
        async with semaphore:
            try:
                async with session.get(url, proxy=proxy_url, timeout=10) as resp:
                    resp.raise_for_status()
                    num_successes += 1
            except:
                pass

    tasks = [fetch(endpoint) for endpoint in endpoints]
    await asyncio.gather(*tasks)
    success_rate = num_successes / len(endpoints)
    print(f'PROXY {i}: {success_rate}')
    return {"proxy_ip": proxy_ip, "success_rate": success_rate}

async def test_all_proxies(proxy_ips, endpoints):
    num_tested = 0
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [test_proxy(i, proxy_ip, endpoints, session, semaphore) for i, proxy_ip in enumerate(proxy_ips)]
        results = await asyncio.gather(*tasks)
        return pd.DataFrame(results)

async def get_success_rates_df():
    proxy_ips = get_raw_proxy_ips()
    results = await test_all_proxies(proxy_ips, endpoints)
    return results

