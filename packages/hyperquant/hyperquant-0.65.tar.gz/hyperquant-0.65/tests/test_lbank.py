import asyncio
import json
import zlib
from aiohttp import ClientWebSocketResponse
import pybotters


def callback(msg, ws: ClientWebSocketResponse = None):
    # print("Received message:", msg)
    decompressed = zlib.decompress(msg, 16 + zlib.MAX_WBITS)
    text = decompressed.decode("utf-8")
    print(f"Decoded text: {text}")

def callback2(msg, ws: ClientWebSocketResponse = None):
    # print("Received message:", msg)
    # print(str(msg))
    data = json.loads(msg)  
    print(data.get('y'))


async def main():
    async with pybotters.Client() as client:
        # webData2
        client.ws_connect(
            "wss://ccws.rerrkvifj.com/ws/V3/",
            send_json={
                "dataType": 3,
                "depth": 200,
                "pair": "arb_usdt",
                "action": "subscribe",
                "subscribe": "depth",
                "msgType": 2,
                "limit": 10,
                "type": 10000,
            },
            hdlr_bytes=callback,
        )

        while True:
            await asyncio.sleep(1)


async def main2():
    async with pybotters.Client() as client:
        # webData2
        # x 为chanel, y为唯一标识, a为参数, z为版本号
        wsapp = client.ws_connect(
            "wss://uuws.rerrkvifj.com/ws/v3",
            send_json={'x': 3, 'y': '3000000001', 'a': {'i': 'SOLUSDT_0.01_25'}, 'z': 1},
            hdlr_bytes=callback2,
        )
        await wsapp._event.wait()

        async with pybotters.Client() as client2:
            client2.ws_connect(
                "wss://uuws.rerrkvifj.com/ws/v3",
                send_json={'x': 3, 'y': '3000000002', 'a': {'i': 'XRPUSDT_0.0001_25'}, 'z': 1},
                hdlr_bytes=callback2,
            )
            await wsapp.current_ws.send_json({'x': 3, 'y': '3000000002', 'a': {'i': 'XRPUSDT_0.0001_25'}, 'z': 1})

        while True:
            await asyncio.sleep(1)

from hyperquant.broker.lbank import Lbank

async def test_broker():
    async with pybotters.Client() as client:
        async with Lbank(client) as lb:
            print(lb.store.detail.find())


async def test_broker_detail():
    async with pybotters.Client() as client: 
        data = await client.post(
            "https://uuapi.rerrkvifj.com/cfd/agg/v1/instrument",
            headers={"source": "4", "versionflage": "true"},
            json={
            "ProductGroup": "SwapU"
            }
        ) 
        res = await data.json()
        print(res)

async def test_broker_subbook():
    async with pybotters.Client() as client:
        async with Lbank(client) as lb:
            symbols = [item['symbol'] for item in lb.store.detail.find()]
            symbols = symbols[10:30]
            print(symbols)

            await lb.sub_orderbook(symbols, limit=1)
            
            while True:
                print(lb.store.book.find({
                    "s": symbols[8]
                }))
                await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_broker_subbook())
