import asyncio
from get_success_rates import get_success_rates_df
from filter_proxies import filter_by_success_rate


async def main():
    df = await get_success_rates_df()
    df = filter_by_success_rate(df)

asyncio.run(main())
