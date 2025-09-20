from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Awaitable, TYPE_CHECKING

from aiohttp import ClientResponse
from pybotters.store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    from pybotters.typedefs import Item
    from pybotters.ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


def _accuracy_to_step(accuracy: int | str | None) -> str:
    try:
        n = int(accuracy) if accuracy is not None else 0
    except (TypeError, ValueError):  # pragma: no cover - defensive guard
        n = 0
    if n <= 0:
        return "1"
    return "0." + "0" * (n - 1) + "1"


class Book(DataStore):
    """LBank order book store parsed from the depth channel."""

    _KEYS = ["id", "S", "p"]

    def _init(self) -> None:
        self.limit: int | None = None
        self.symbol_map: dict[str, str] = {}




    def _on_message(self, msg: Any) -> None:
        
        data = json.loads(msg)
        
        if not data:
            return

        channel_id = None
        if data.get("y") is not None:
            channel_id = str(data["y"])

        symbol = None
        if channel_id:
            symbol = self.symbol_map.get(channel_id)
        if symbol is None and data.get("i"):
            symbol = self.symbol_map.get(str(data["i"]))

        bids = data.get("b", [])
        asks = data.get("s", [])
        if not (bids or asks):
            return
        bids = bids[: self.limit] if self.limit else bids
        asks = asks[: self.limit] if self.limit else asks
        bids = [
            {"id": channel_id, "S": "b", "p": str(item[0]), "q": str(item[1]), "s": symbol}
            for item in bids
        ]
        asks = [
            {"id": channel_id, "S": "a", "p": str(item[0]), "q": str(item[1]), "s": symbol}
            for item in asks
        ]


        if channel_id is not None:
            self._find_and_delete({"id": channel_id})
        self._insert(bids + asks)


class Detail(DataStore):
    """Futures instrument metadata store obtained from the futures instrument endpoint."""

    _KEYS = ["symbol"]

    def _transform(self, entry: dict[str, Any]) -> dict[str, Any] | None:
        try:
            instrument:dict = entry["instrument"]
            fee:dict = entry["fee"]
            market_data:dict = entry["marketData"]
        except (KeyError, TypeError):
            return None
        return {
            "symbol": instrument.get("instrumentID"),
            "instrument_name": instrument.get("instrumentName"),
            "base_currency": instrument.get("baseCurrency"),
            "price_currency": instrument.get("priceCurrency"),
            "min_order_volume": instrument.get("minOrderVolume"),
            "max_order_volume": instrument.get("maxOrderVolume"),
            "tick_size": instrument.get("priceTick"),
            "step_size": instrument.get("volumeTick"),
            "maker_fee": fee.get("makerOpenFeeRate"),
            "taker_fee": fee.get("takerOpenFeeRate"),
            "last_price": market_data.get("lastPrice"),
            "amount24": market_data.get("turnover24"),
        }

    def _onresponse(self, data: list[dict[str, Any]] | dict[str, Any] | None) -> None:
        if not data:
            self._clear()
            return
        entries = data
        if isinstance(data, dict):  # pragma: no cover - defensive guard
            entries = data.get("data") or []
        items: list[dict[str, Any]] = []
        for entry in entries or []:
            transformed = self._transform(entry)
            if transformed:
                items.append(transformed)
        if not items:
            self._clear()
            return
        self._clear()
        self._insert(items)


class LbankDataStore(DataStoreCollection):
    """Aggregates book/detail stores for the LBank public feed."""

    def _init(self) -> None:
        self._create("book", datastore_class=Book)
        self._create("detail", datastore_class=Detail)
        self._channel_to_symbol: dict[str, str] = {}

    @property
    def book(self) -> Book:
        """
        订单簿（Order Book）数据流，按订阅ID（channel_id）索引。

        此属性表示通过深度频道（depth channel）接收到的订单簿快照和增量更新，数据结构示例如下：

        Data structure:
            [
                {
                    "id": <channel_id>,
                    "S": "b" 或 "a",  # "b" 表示买单，"a" 表示卖单
                    "p": <价格>,
                    "q": <数量>,
                    "s": <标准化交易对符号>
                },
                ...
            ]

        通过本属性可以获取当前 LBank 订单簿的最新状态，便于后续行情分析和撮合逻辑处理。
        """
        return self._get("book")

    @property
    def detail(self) -> Detail:
        """

        _KEYS = ["symbol"]

        期货合约详情元数据流。

        此属性表示通过期货合约接口获取的合约详情，包括合约ID、合约名称、基础币种、计价币种、最小/最大下单量、价格跳动、交易量跳动、maker/taker手续费率、最新价和24小时成交额等信息。

        Data structure:
            [
                {
                    "symbol": "BTCUSDT",               # 合约ID
                    "instrument_name": "BTCUSDT",      # 合约名称
                    "base_currency": "BTC",            # 基础币种
                    "price_currency": "USDT",          # 计价币种
                    "min_order_volume": "0.0001",        # 最小下单量
                    "max_order_volume": "600.0",         # 最大下单量
                    "tick_size": "0.1",                  # 最小价格变动单位
                    "step_size": "0.0001",               # 最小数量变动单位
                    "maker_fee": "0.0002",               # Maker 手续费率
                    "taker_fee": "0.0006",               # Taker 手续费率
                    "last_price": "117025.5",            # 最新价
                    "amount24": "807363493.97579747"     # 24小时成交额
                },
                ...
            ]

        通过本属性可以获取所有支持的期货合约元数据，便于下单参数校验和行情展示。
        """
        return self._get("detail")


    def register_book_channel(self, channel_id: str, symbol: str, *, raw_symbol: str | None = None) -> None:
        if channel_id is not None:
            self.book.symbol_map[str(channel_id)] = symbol
        if raw_symbol:
            self.book.symbol_map[str(raw_symbol)] = symbol


    async def initialize(self, *aws: Awaitable[ClientResponse]) -> None:
        for fut in asyncio.as_completed(aws):
            res = await fut
            data = await res.json()
            if res.url.path == "/cfd/agg/v1/instrument":
                self.detail._onresponse(data)


    def onmessage(self, msg: Item, ws: ClientWebSocketResponse | None = None) -> None:
        self.book._on_message(msg)
