from __future__ import annotations

import time
from typing import Any, Iterable, Literal

import pybotters

from .models.edgex import EdgexDataStore


class Edgex:
    """
    Edgex 公共 API (HTTP/WS) 封装。

    说明
    - 当前仅包含公共行情数据（不包含私有接口）。
    - 订单簿频道命名规则：``depth.{contractId}.{level}``。
      成功订阅后，服务器会先推送一次完整快照（depthType=SNAPSHOT），之后持续推送增量（depthType=CHANGED）。
      解析后的结果存入 ``EdgexDataStore.book``。

    参数
    - client: ``pybotters.Client`` 实例
    - api_url: REST 基地址；默认使用 Edgex 官方 testnet 站点
    - ws_url: WebSocket 基地址；如不提供，则默认使用官方文档地址。
    """

    def __init__(
        self,
        client: pybotters.Client,
        *,
        api_url: str | None = None,
    ) -> None:
        self.client = client
        self.store = EdgexDataStore()
        # 公共端点可能因环境/地区不同而变化，允许外部覆盖。
        self.api_url = api_url or "https://pro.edgex.exchange"
        self.ws_url = "wss://quote.edgex.exchange"

    async def __aenter__(self) -> "Edgex":
        # 初始化基础合约元数据，便于后续使用 tickSize 等字段。
        await self.update_detail()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: BaseException | None,
    ) -> None:
        # Edgex 当前没有需要关闭的资源；保持接口与 Ourbit 等类一致。
        return None

    async def update_detail(self) -> dict[str, Any]:
        """Fetch and cache contract metadata via the public REST endpoint."""

        url = self._resolve_api_path("/api/v1/public/meta/getMetaData")
        res = await self.client.get(url)
        res.raise_for_status()
        data = await res.json()

        if data.get("code") != "SUCCESS":  # pragma: no cover - defensive guard
            raise RuntimeError(f"Failed to fetch Edgex metadata: {data}")

        self.store._apply_metadata(data)
        return data

    def _resolve_api_path(self, path: str) -> str:
        base = (self.api_url or "").rstrip("/")
        return f"{base}{path}"

    async def sub_orderbook(
        self,
        contract_ids: str | Iterable[str] | None = None,
        *,
        symbols: str | Iterable[str] | None = None,
        level: int = 15,
        ws_url: str | None = None,
    ) -> None:
        """订阅指定合约 ID 或交易对名的订单簿（遵循 Edgex 协议）。

        规范
        - 默认 WS 端点：wss://quote.edgex.exchange（可通过参数/实例覆盖）
        - 每个频道的订阅报文：
          {"type": "subscribe", "channel": "depth.{contractId}.{level}"}
        - 服务端在订阅成功后，会先推送一次快照，再持续推送增量。
        """

        ids: list[str] = []
        if contract_ids is not None:
            if isinstance(contract_ids, str):
                ids.extend([contract_ids])
            else:
                ids.extend(contract_ids)

        if symbols is not None:
            if isinstance(symbols, str):
                lookup_symbols = [symbols]
            else:
                lookup_symbols = list(symbols)

            for symbol in lookup_symbols:
                matches = self.store.detail.find({"contractName": symbol})
                if not matches:
                    raise ValueError(f"Unknown Edgex symbol: {symbol}")
                ids.append(str(matches[0]["contractId"]))

        if not ids:
            raise ValueError("contract_ids or symbols must be provided")

        channels = [f"depth.{cid}.{level}" for cid in ids]

        # 优先使用参数 ws_url，其次使用实例的 ws_url，最后使用默认地址。
        url =  f"{self.ws_url}/api/v1/public/ws?timestamp=" + str(int(time.time() * 1000))

        # 根据文档：每个频道一条订阅指令，允许一次发送多个订阅对象。
        payload = [{"type": "subscribe", "channel": ch} for ch in channels]

        wsapp = self.client.ws_connect(url, send_json=payload, hdlr_json=self.store.onmessage)
        # 等待 WS 完成握手再返回，确保订阅报文成功发送。
        await wsapp._event.wait()

    async def sub_ticker(
        self,
        contract_ids: str | Iterable[str] | None = None,
        *,
        symbols: str | Iterable[str] | None = None,
        all_contracts: bool = False,
        periodic: bool = False,
        ws_url: str | None = None,
    ) -> None:
        """订阅 24 小时行情推送。

        参数
        - contract_ids / symbols: 指定单个或多个合约；二者至少提供一个。
        - all_contracts: 订阅 ``ticker.all``（或 ``ticker.all.1s``）。
        - periodic: 与 ``all_contracts`` 配合，true 则订阅 ``ticker.all.1s``。
        """

        channels: list[str] = []

        if all_contracts:
            channel = "ticker.all.1s" if periodic else "ticker.all"
            channels.append(channel)
        else:
            ids: list[str] = []
            if contract_ids is not None:
                if isinstance(contract_ids, str):
                    ids.append(contract_ids)
                else:
                    ids.extend(contract_ids)

            if symbols is not None:
                if isinstance(symbols, str):
                    lookup_symbols = [symbols]
                else:
                    lookup_symbols = list(symbols)

                for symbol in lookup_symbols:
                    matches = self.store.detail.find({"contractName": symbol})
                    if not matches:
                        raise ValueError(f"Unknown Edgex symbol: {symbol}")
                    ids.append(str(matches[0]["contractId"]))

            if not ids:
                raise ValueError("Provide contract_ids/symbols or set all_contracts=True")

            channels.extend(f"ticker.{cid}" for cid in ids)

        url = ws_url or f"{self.ws_url}/api/v1/public/ws?timestamp=" + str(int(time.time() * 1000))
        payload = [{"type": "subscribe", "channel": ch} for ch in channels]

        wsapp = self.client.ws_connect(url, send_json=payload, hdlr_json=self.store.onmessage)
        await wsapp._event.wait()


    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: BaseException | None,
    ) -> None:
        # Edgex 当前没有需要关闭的资源；保持接口与 Ourbit 等类一致。
        return None