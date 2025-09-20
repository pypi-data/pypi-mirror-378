from __future__ import annotations

import asyncio
import itertools
import json
import logging
import time
import zlib
from typing import Iterable, Literal

import pybotters

from .models.lbank import LbankDataStore

logger = logging.getLogger(__name__)

# https://ccapi.rerrkvifj.com 似乎是spot的api
# https://uuapi.rerrkvifj.com 似乎是合约的api


class Lbank:
    """LBank public market-data client (REST + WS)."""

    def __init__(
        self,
        client: pybotters.Client,
        *,
        front_api: str | None = None,
        rest_api: str | None = None,
        ws_url: str | None = None,
    ) -> None:
        self.client = client
        self.store = LbankDataStore()
        self.front_api = front_api or "https://uuapi.rerrkvifj.com"
        self.rest_api = rest_api or "https://api.lbkex.com"
        self.ws_url = ws_url or "wss://uuws.rerrkvifj.com/ws/v3"
        self._req_id = itertools.count(int(time.time() * 1000))
        self._ws_app = None

    async def __aenter__(self) -> "Lbank":
        await self.update("detail")
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        pass

    async def update(self, update_type: Literal["detail", "ticker", "all"]) -> list[dict]:
        all_urls = [f"{self.front_api}/cfd/agg/v1/instrument"]
        url_map = {"detail": [all_urls[0]], "all": all_urls}


        try:
            urls = url_map[update_type]
        except KeyError:
            raise ValueError(f"update_type err: {update_type}")

        # await self.store.initialize(*(self.client.get(url) for url in urls))
        if update_type == "detail" or update_type == "all":
            await self.store.initialize(
                self.client.post(
                    all_urls[0],
                    json={"ProductGroup": "SwapU"},
                    headers={"source": "4", "versionflage": "true"},
                )
            )


    async def sub_orderbook(self, symbols: list[str], limit: int | None = None) -> None:
        """订阅指定交易对的订单簿（遵循 LBank 协议）。
        """

        async def sub(payload):
            wsapp = self.client.ws_connect(
                self.ws_url,
                hdlr_bytes=self.store.onmessage,
                send_json=payload,
            )
            await wsapp._event.wait()

        send_jsons = []
        y = 3000000001
        if limit:
            self.store.book.limit = limit

        for symbol in symbols:

            info = self.store.detail.get({"symbol": symbol})
            if not info:
                raise ValueError(f"Unknown LBank symbol: {symbol}")
            
            tick_size = info['tick_size']
            sub_i = symbol + "_" + str(tick_size) + "_25"
            send_jsons.append(
                {
                    "x": 3,
                    "y": str(y),
                    "a": {"i": sub_i},
                    "z": 1,
                }
            )

            self.store.register_book_channel(str(y), symbol)
            y += 1

        # Rate limit: max 5 subscriptions per second
        for i in range(0, len(send_jsons), 5):
            batch = send_jsons[i:i+5]
            await asyncio.gather(*(sub(send_json) for send_json in batch))
            if i + 5 < len(send_jsons):
                await asyncio.sleep(0.1)