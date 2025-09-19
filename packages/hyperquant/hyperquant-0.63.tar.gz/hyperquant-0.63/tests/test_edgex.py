from hyperquant.broker.edgex import Edgex
import pybotters
async def main():
    async with pybotters.Client() as client:
        async with Edgex(client) as broker:
            # print(broker.store.detail.find({
            #     'contractName': 'BTCUSD',
            # }))

            await broker.sub_orderbook(symbols=['BTCUSD'])
            broker.store.book.limit = 1
            while True:
               print(broker.store.book.find({"S": 'b'}))
               await asyncio.sleep(1)

            # await broker.sub_ticker(all_contracts=True, periodic=True)
            # broker.store.book.limit = 1
            # while True:
            #     print(broker.store.ticker.find({
            #         's':'BTCUSD',
            #     }))
            #     await asyncio.sleep(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())