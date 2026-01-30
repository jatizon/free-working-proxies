# Working Free Proxies

A utility built on top of [TheSpeedX/PROXY-List](https://github.com/TheSpeedX/PROXY-List). It fetches the proxies from that repository, tests each one against multiple endpoints, and writes them into separate files by **working status** and **connection quality**.

The proxy list is refreshed and re-tested **automatically every 1 hour** (via GitHub Actions), so the output files stay up to date without manual runs.

---

## Upstream: TheSpeedX/PROXY-List

This project uses [TheSpeedX/PROXY-List](https://github.com/TheSpeedX/PROXY-List) as its data source. That repository maintains free public HTTP, SOCKS4, and SOCKS5 proxy lists that are updated regularly. The lists are plain-text files (e.g. `http.txt`) with one proxy per line (`host:port`).

We pull the **HTTP** list from:

- `https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt`

Only HTTP proxies are tested and categorized by this tool. The upstream list is for educational use; credits and stars to the original project are appreciated.

---

## How It Works

### 1. Fetch raw proxies (`get_success_rates.py`)

- **`get_raw_proxy_ips()`**  
  Downloads the HTTP proxy list from TheSpeedX/PROXY-List and returns a list of `host:port` strings.

### 2. Test each proxy

- Each proxy is tested by sending HTTP requests through it to several public endpoints:
  - `https://api.ipify.org?format=json`
  - `https://ifconfig.me/ip`
  - `https://checkip.amazonaws.com`
  - `https://httpbin.org/get`
  - `https://postman-echo.com/get`
  - `https://www.google.com`
  - `https://www.cloudflare.com`

- Requests are done **asynchronously** with `aiohttp`, with a concurrency limit (`MAX_CONCURRENT=200`) and a 10-second timeout per request.
- For each proxy, the script counts how many of these requests succeed and computes a **success rate** (0 to 1).

### 3. Categorize by success rate (`filter_proxies.py`)

- **`filter_by_success_rate()`** assigns a status from the success rate:
  - **NOT WORKING** — success rate `0`
  - **BAD** — success rate &lt; `0.7`
  - **GOOD** — success rate &lt; `0.9`
  - **VERY_GOOD** — success rate ≥ `0.9`

- Proxies with status **BAD**, **GOOD**, or **VERY_GOOD** are written to CSV files in the `proxies/` directory (by default `../proxies` relative to the script):
  - `bad_proxies.csv`
  - `good_proxies.csv`
  - `very_good_proxies.csv`

- **NOT WORKING** proxies are not written to any file; they are only present in the in-memory DataFrame.

### 4. Entry point (`main.py`)

- **`main()`** runs the pipeline:
  1. `get_success_rates_df()` — fetch proxies and test them → DataFrame with `proxy_ip` and `success_rate`.
  2. `filter_by_success_rate(df)` — add `status` and write the three CSVs.

---

## Automatic updates (every 1 hour)

A **GitHub Actions** workflow runs on a schedule **every hour**. It:

1. Checks out the repo.
2. Sets up Python and installs dependencies.
3. Runs the script from the project root (so `proxies/` is created in the repo).
4. Commits and pushes the updated `proxies/*.csv` files so the latest working proxies are always in the repository.

So the proxy lists in this repo are refreshed and re-tested automatically every 1 hour without any manual action.

---

## Requirements

- Python 3.7+
- `pandas`
- `aiohttp`
- `requests`

---

## Usage

From the project root:

```bash
pip install pandas aiohttp requests
python src/main.py
```

Output CSVs will appear in `proxies/` (or the path you pass to `filter_by_success_rate()`).

---

## Output

| File               | Description                          |
|--------------------|--------------------------------------|
| `proxies/bad_proxies.csv`      | Success rate &lt; 70%                |
| `proxies/good_proxies.csv`     | Success rate 70%–89%                 |
| `proxies/very_good_proxies.csv`| Success rate ≥ 90%                   |

Each CSV has columns: `proxy_ip`, `success_rate`, and `status`.
