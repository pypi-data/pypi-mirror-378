from __future__ import annotations

import asyncio
from typing import Any, Awaitable, TYPE_CHECKING

from aiohttp import ClientResponse
from pybotters.store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    from pybotters.typedefs import Item
    from pybotters.ws import ClientWebSocketResponse


class Book(DataStore):
    """Order book data store for the Edgex websocket feed."""

    _KEYS = ["c", "S", "p"]

    def _init(self) -> None:
        self._version: int | str | None = None
        self.limit: int | None = None

    def _on_message(self, msg: dict[str, Any]) -> None:
        content = msg.get("content") or {}
        entries = content.get("data") or []
        data_type = (content.get("dataType") or "").lower()

        for entry in entries:
            contract_id = entry.get("contractId")
            if contract_id is None:
                continue

            contract_name = entry.get("contractName")
            end_version = entry.get("endVersion")
            depth_type = (entry.get("depthType") or "").lower()

            is_snapshot = data_type == "snapshot" or depth_type == "snapshot"

            if is_snapshot:
                self._handle_snapshot(
                    contract_id,
                    contract_name,
                    entry,
                )
            else:
                self._handle_delta(
                    contract_id,
                    contract_name,
                    entry,
                )

            if end_version is not None:
                self._version = self._normalize_version(end_version)

    def _handle_snapshot(
        self,
        contract_id: str,
        contract_name: str | None,
        entry: dict[str, Any],
    ) -> None:
        asks = entry.get("asks") or []
        bids = entry.get("bids") or []

        self._find_and_delete({"c": contract_id})

        payload: list[dict[str, Any]] = []
        payload.extend(
            self._build_items(
                contract_id,
                contract_name,
                "a",
                asks,
            )
        )
        payload.extend(
            self._build_items(
                contract_id,
                contract_name,
                "b",
                bids,
            )
        )

        if payload:
            self._insert(payload)
            self._trim(contract_id, contract_name)

    def _handle_delta(
        self,
        contract_id: str,
        contract_name: str | None,
        entry: dict[str, Any],
    ) -> None:
        updates: list[dict[str, Any]] = []
        deletes: list[dict[str, Any]] = []

        asks = entry.get("asks") or []
        bids = entry.get("bids") or []

        for side, levels in (("a", asks), ("b", bids)):
            for row in levels:
                price, size = self._extract_price_size(row)
                criteria = {"c": contract_id, "S": side, "p": price}

                if not size or float(size) == 0.0:
                    deletes.append(criteria)
                    continue

                updates.append(
                    {
                        "c": contract_id,
                        "S": side,
                        "p": price,
                        "q": size,
                        "s": self._symbol(contract_id, contract_name),
                    }
                )

        if deletes:
            self._delete(deletes)
        if updates:
            self._update(updates)
            self._trim(contract_id, contract_name)
        

    def _build_items(
        self,
        contract_id: str,
        contract_name: str | None,
        side: str,
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for row in rows:
            price, size = self._extract_price_size(row)
            if not size or float(size) == 0.0:
                continue
            items.append(
                {
                    "c": contract_id,
                    "S": side,
                    "p": price,
                    "q": size,
                    "s": self._symbol(contract_id, contract_name),
                }
            )
        return items

    @staticmethod
    def _normalize_version(value: Any) -> int | str:
        if value is None:
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            return str(value)

    @staticmethod
    def _to_str(value: Any) -> str | None:
        if value is None:
            return None
        return str(value)

    @staticmethod
    def _extract_price_size(row: dict[str, Any]) -> tuple[str, str]:
        return str(row["price"]), str(row["size"])

    def _trim(self, contract_id: str, contract_name: str | None) -> None:
        if self.limit is None:
            return

        query: dict[str, Any]
        symbol = self._symbol(contract_id, contract_name)
        if symbol:
            query = {"s": symbol}
        else:
            query = {"c": contract_id}

        sort_data = self.sorted(query, self.limit)
        asks = sort_data.get("a", [])
        bids = sort_data.get("b", [])

        self._find_and_delete(query)

        trimmed = asks + bids
        if trimmed:
            self._insert(trimmed)

    @staticmethod
    def _symbol(contract_id: str, contract_name: str | None) -> str:
        if contract_name:
            return str(contract_name)
        return str(contract_id)

    @property
    def version(self) -> int | str | None:
        """返回当前缓存的订单簿版本号。"""
        return self._version

    def sorted(
        self,
        query: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """按买卖方向与价格排序后的订单簿视图。"""
        return self._sorted(
            item_key="S",
            item_asc_key="a",
            item_desc_key="b",
            sort_key="p",
            query=query,
            limit=limit,
        )


class Ticker(DataStore):
    """24 小时行情推送数据。"""

    _KEYS = ["c"]

    def _on_message(self, msg: dict[str, Any]) -> None:
        content = msg.get("content") or {}
        entries = content.get("data") or []
        data_type = (content.get("dataType") or "").lower()

        for entry in entries:
            item = self._format(entry)
            if item is None:
                continue

            criteria = {"c": item["c"]}
            if data_type == "snapshot":
                self._find_and_delete(criteria)
                self._insert([item])
            else:
                self._update([item])

    def _format(self, entry: dict[str, Any]) -> dict[str, Any] | None:
        contract_id = entry.get("contractId")
        if contract_id is None:
            return None

        item: dict[str, Any] = {"c": str(contract_id)}

        name = entry.get("contractName")
        if name is not None:
            item["s"] = str(name)

        fields = [
            "priceChange",
            "priceChangePercent",
            "trades",
            "size",
            "value",
            "high",
            "low",
            "open",
            "close",
            "highTime",
            "lowTime",
            "startTime",
            "endTime",
            "lastPrice",
            "indexPrice",
            "oraclePrice",
            "openInterest",
            "fundingRate",
            "fundingTime",
            "nextFundingTime",
            "bestAskPrice",
            "bestBidPrice",
        ]

        for key in fields:
            value = entry.get(key)
            if value is not None:
                item[key] = str(value)

        return item


class CoinMeta(DataStore):
    """Coin metadata (precision, StarkEx info, etc.)."""

    _KEYS = ["coinId"]

    def _onresponse(self, data: dict[str, Any]) -> None:
        coins = (data.get("data") or {}).get("coinList") or []
        items: list[dict[str, Any]] = []

        for coin in coins:
            coin_id = coin.get("coinId")
            if coin_id is None:
                continue
            items.append(
                {
                    "coinId": str(coin_id),
                    "coinName": coin.get("coinName"),
                    "stepSize": coin.get("stepSize"),
                    "showStepSize": coin.get("showStepSize"),
                    "starkExAssetId": coin.get("starkExAssetId"),
                }
            )

        self._clear()
        if items:
            self._insert(items)


class ContractMeta(DataStore):
    """Per-contract trading parameters from the metadata endpoint."""

    _KEYS = ["contractId"]

    _FIELDS = (
        "contractName",
        "baseCoinId",
        "quoteCoinId",
        "tickSize",
        "stepSize",
        "minOrderSize",
        "maxOrderSize",
        "defaultTakerFeeRate",
        "defaultMakerFeeRate",
        "enableTrade",
        "fundingInterestRate",
        "fundingImpactMarginNotional",
        "fundingRateIntervalMin",
        "starkExSyntheticAssetId",
        "starkExResolution",
    )

    def _onresponse(self, data: dict[str, Any]) -> None:
        contracts = (data.get("data") or {}).get("contractList") or []
        items: list[dict[str, Any]] = []

        for contract in contracts:
            contract_id = contract.get("contractId")
            if contract_id is None:
                continue

            payload = {"contractId": str(contract_id)}
            for key in self._FIELDS:
                payload[key] = contract.get(key)
            payload["riskTierList"] = self._simplify_risk_tiers(contract.get("riskTierList"))

            items.append(payload)

        self._clear()
        if items:
            self._insert(items)

    @staticmethod
    def _simplify_risk_tiers(risk_tiers: Any) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for tier in risk_tiers or []:
            items.append(
                {
                    "tier": tier.get("tier"),
                    "positionValueUpperBound": tier.get("positionValueUpperBound"),
                    "maxLeverage": tier.get("maxLeverage"),
                    "maintenanceMarginRate": tier.get("maintenanceMarginRate"),
                    "starkExRisk": tier.get("starkExRisk"),
                    "starkExUpperBound": tier.get("starkExUpperBound"),
                }
            )
        return items

class EdgexDataStore(DataStoreCollection):
    """Edgex DataStore collection exposing the order book feed."""

    def _init(self) -> None:
        self._create("book", datastore_class=Book)
        self._create("ticker", datastore_class=Ticker)
        self._create("meta_coin", datastore_class=CoinMeta)
        self._create("detail", datastore_class=ContractMeta)

    @property
    def book(self) -> Book:
        """
        获取 Edgex 合约订单簿数据流。

        .. code:: json

            [
                {
                    "c": "10000001",        # 合约 ID
                    "s": "BTCUSD",
                    "S": "a",               # 方向 a=卖 b=买
                    "p": "117388.2",        # 价格
                    "q": "12.230",          # 数量
                }
            ]
        """
        return self._get("book")



    @property
    def coins(self) -> CoinMeta:
        """
        获取币种精度及 StarkEx 资产信息列表。

        .. code:: json

            [
                {
                    "coinId": "1000",
                    "coinName": "USDT",
                    "stepSize": "0.000001",
                    "showStepSize": "0.0001",
                    "starkExAssetId": "0x33bda5c9..."
                }
            ]
        """
        return self._get("meta_coin")

    @property
    def detail(self) -> ContractMeta:
        """
        获取合约级别的交易参数。

        .. code:: json

            [
                {
                    "contractId": "10000001",
                    "contractName": "BTCUSDT",
                    "baseCoinId": "1001",
                    "quoteCoinId": "1000",
                    "tickSize": "0.1",
                    "stepSize": "0.001",
                    "minOrderSize": "0.001",
                    "maxOrderSize": "50.000",
                    "defaultMakerFeeRate": "0.0002",
                    "defaultTakerFeeRate": "0.00055",
                    "enableTrade": true,
                    "fundingInterestRate": "0.0003",
                    "fundingImpactMarginNotional": "10",
                    "fundingRateIntervalMin": "240",
                    "starkExSyntheticAssetId": "0x42544332...",
                    "starkExResolution": "0x2540be400",
                    "riskTierList": [
                        {
                            "tier": 1,
                            "positionValueUpperBound": "50000",
                            "maxLeverage": "100",
                            "maintenanceMarginRate": "0.005",
                            "starkExRisk": "21474837",
                            "starkExUpperBound": "214748364800000000000"
                        }
                    ]
                }
            ]
        """
        return self._get("detail")

    @property
    def ticker(self) -> Ticker:
        """
        获取 24 小时行情推送。

        .. code:: json

            [
                {
                    "c": "10000001",      # 合约 ID
                    "s": "BTCUSD",        # 合约名称
                    "lastPrice": "117400",  # 最新价
                    "priceChange": "200",   # 涨跌额
                    "priceChangePercent": "0.0172",  # 涨跌幅
                    "size": "1250",        # 24h 成交量
                    "value": "147000000", # 24h 成交额
                    "high": "118000",      # 24h 最高价
                    "low": "116500",       # 低价
                    "open": "116800",      # 开盘价
                    "close": "117400",     # 收盘价
                    "indexPrice": "117350", # 指数价
                    "oraclePrice": "117360.12", # 预言机价
                    "openInterest": "50000",    # 持仓量
                    "fundingRate": "0.000234",  # 当前资金费率
                    "fundingTime": "1758240000000", # 上一次结算时间
                    "nextFundingTime": "1758254400000", # 下一次结算时间
                    "bestAskPrice": "117410",    # 卖一价
                    "bestBidPrice": "117400"     # 买一价
                }
            ]
        """
        return self._get("ticker")

    async def initialize(self, *aws: Awaitable["ClientResponse"]) -> None:
        """Populate metadata stores from awaited HTTP responses."""

        for fut in asyncio.as_completed(aws):
            res = await fut
            data = await res.json()
            if res.url.path == "/api/v1/public/meta/getMetaData":
                self._apply_metadata(data)

    def onmessage(self, msg: Item, ws: ClientWebSocketResponse | None = None) -> None:
        channel = (msg.get("channel") or "").lower()
        msg_type = (msg.get("type") or "").lower()

        if msg_type == "ping" and ws is not None:
            payload = {"type": "pong", "time": msg.get("time")}
            asyncio.create_task(ws.send_json(payload))
            return

        if "depth" in channel and msg_type in {"quote-event", "payload"}:
            self.book._on_message(msg)

        if channel.startswith("ticker") and msg_type in {"payload", "quote-event"}:
            self.ticker._on_message(msg)


    def _apply_metadata(self, data: dict[str, Any]) -> None:
        self.coins._onresponse(data)
        self.detail._onresponse(data)
