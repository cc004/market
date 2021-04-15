from asyncio.events import get_event_loop
from asyncio.tasks import run_coroutine_threadsafe
from traceback import format_exc
from nonebot import scheduler
from pytz import timezone
from hoshino.aiorequests import get

class product:
    def __init__(self, name, multiplier):
        self.name = name
        self.price_cache = None
        self.multiplier = multiplier
    
    @property
    def price(self) -> float:
        if self.price_cache == None:
            raise RuntimeError
        return self.price_cache

    @property
    def interval(self) -> float:
        return 5

    @property
    async def _price(self) -> float:
        raise NotImplementedError
    
    async def _schedule_wrapper(self):
        try:
            self.price_cache = self.multiplier * await self._price
        except Exception as e:
            self.logger.error(f'exception while caching {self.name}:\n{format_exc()}')

    def schedule(self):

        run_coroutine_threadsafe(self._schedule_wrapper(), get_event_loop())

        scheduler.scheduled_job(
            'interval',
            minutes=self.interval,
            timezone=timezone('Asia/Shanghai'),
            misfire_grace_time=60,
            coalesce=True
        )(self._schedule_wrapper)

class api_product(product):
    @property
    def timeout(self) -> float:
        return 10

    @property
    def url(self) -> str:
        raise NotImplementedError

    def converter(self, text) -> object:
        raise NotImplementedError

    @property
    async def _price(self) -> float:
        return float(self.converter(await (await get(self.url, timeout=self.timeout)).text))

class sina_product(api_product):
    def __init__(self, id, name, multiplier=1.0):
        self.id = id
        super().__init__(name, multiplier)
    
    @property
    def url(self) -> str:
        return f"http://hq.sinajs.cn/list={self.id}"

    def converter(self, text) -> object:
        return text.split(',')[3]

import json

class coincap_product(api_product):
    def __init__(self, id, name, multiplier=1.0):
        self.id = id
        super().__init__(name, multiplier)
        
    @property
    def url(self) -> str:
        return f"https://api.coincap.io/v2/assets/{self.id}"

    def converter(self, text) -> object:
        return json.loads(text)['data']['priceUsd']

class sochain_product(api_product):
    def __init__(self, id, name, multiplier=1.0):
        ids = id.split(':')
        self.coin = ids[0]
        self.base = ids[1]
        super().__init__(name, multiplier)
            
    @property
    def url(self) -> str:
        return f"https://sochain.com/api/v2/get_price/{self.coin}/{self.base}"

    def converter(self, text) -> object:
        return json.loads(text)['data']['prices'][0]['price']

class cryptocompare_product(api_product):
    def __init__(self, id, name, multiplier=1.0):
        ids = id.split(':')
        self.coin = ids[0]
        self.base = ids[1]
        super().__init__(name, multiplier)
            
    @property
    def url(self) -> str:
        return f"https://min-api.cryptocompare.com/data/price?fsym={self.coin}&tsyms={self.base}"

    def converter(self, text) -> object:
        return [x for x in json.loads(text).values()][0]