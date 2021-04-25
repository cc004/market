from asyncio.events import get_event_loop
from asyncio.tasks import run_coroutine_threadsafe
from traceback import format_exc
from nonebot import scheduler
from pytz import timezone
from hoshino.aiorequests import get
from hoshino.log import new_logger

class product:
    def __init__(self, name):
        self.name = name
        self.logger = new_logger(name)
    @property
    def price(self) -> float:
        raise NotImplemented

    def schedule(self):
        raise NotImplemented

class multiplier_product(product):
    def __init__(self, base: product, multiplier):
        self.base = base
        self.multiplier = multiplier
        super().__init__(self.base.name)

    @property
    def price(self) -> float:
        return self.base.price * self.multiplier

    def schedule(self):
        self.base.schedule()

class cached_product:
    def __init__(self, name):
        self.name = name
        self.price_cache = None
    
    @property
    def price(self) -> float:
        if self.price_cache == None:
            raise RuntimeError
        return self.price_cache

    @property
    def _interval(self) -> float:
        return 5

    @property
    async def _price(self) -> float:
        raise NotImplementedError
    
    async def _schedule_wrapper(self):
        try:
            self.price_cache = await self._price
        except Exception as e:
            self.logger.error(f'exception while caching {self.name}:\n{format_exc()}')

    def schedule(self):

        run_coroutine_threadsafe(self._schedule_wrapper(), get_event_loop())

        scheduler.scheduled_job(
            'interval',
            minutes=self._interval,
            timezone=timezone('Asia/Shanghai'),
            misfire_grace_time=60,
            coalesce=True
        )(self._schedule_wrapper)

class api_product(cached_product):
    @property
    def _timeout(self) -> float:
        return 10

    @property
    def _url(self) -> str:
        raise NotImplementedError

    def _converter(self, text) -> object:
        raise NotImplementedError

    @property
    async def _price(self) -> float:
        return float(self._converter(await (await get(self._url, timeout=self._timeout)).text))

class sina_product(api_product):
    def __init__(self, id, name):
        self.id = id
        super().__init__(name)
    
    @property
    def _url(self) -> str:
        return f"http://hq.sinajs.cn/list={self.id}"

    def _converter(self, text) -> object:
        return text.split(',')[3]

import json

class coincap_product(api_product):
    def __init__(self, id, name):
        self.id = id
        super().__init__(name)
        
    @property
    def _url(self) -> str:
        return f"https://api.coincap.io/v2/assets/{self.id}"

    def _converter(self, text) -> object:
        return json.loads(text)['data']['priceUsd']

class sochain_product(api_product):
    def __init__(self, id, name):
        ids = id.split(':')
        self.coin = ids[0]
        self.base = ids[1]
        super().__init__(name)
            
    @property
    def _url(self) -> str:
        return f"https://sochain.com/api/v2/get_price/{self.coin}/{self.base}"

    def _converter(self, text) -> object:
        return json.loads(text)['data']['prices'][0]['price']

class cryptocompare_product(api_product):
    def __init__(self, id, name):
        ids = id.split(':')
        self.coin = ids[0]
        self.base = ids[1]
        super().__init__(name)
            
    @property
    def _url(self) -> str:
        return f"https://min-api.cryptocompare.com/data/price?fsym={self.coin}&tsyms={self.base}"

    def converter(self, text) -> object:
        return [x for x in json.loads(text).values()][0]