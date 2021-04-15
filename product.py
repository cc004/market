from asyncio.events import get_event_loop
from asyncio.tasks import run_coroutine_threadsafe

from nonebot import scheduler
from pytz import timezone
from hoshino.aiorequests import get

class product:
    def __init__(self, name):
        self.name = name
        self.price_cache = None
    
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
            self.price_cache = await self._price
        except Exception as e:
            self.logger.error(f'exception while caching {self.name}:\n{e}')

    def schedule(self):

        run_coroutine_threadsafe(self._schedule_wrapper(), get_event_loop())

        scheduler.scheduled_job(
            'interval',
            minutes=self.interval,
            timezone=timezone('Asia/Shanghai'),
            misfire_grace_time=60,
            coalesce=True
        )(self._schedule_wrapper)

class sina_product(product):
    def __init__(self, id, name):
        self.id = id
        super().__init__(name)
    
    @property
    async def _price(self) -> float:
        return float((await (await get("http://hq.sinajs.cn/list=" + self.id)).content).decode('gbk').split(',')[3])

import json

class coincap_product(product):
    def __init__(self, id, name):
        self.id = id
        super().__init__(name)
    
    @property
    async def _price(self) -> float:
        return json.loads(await (await get("https://api.coincap.io/v2/assets/" + self.id)).content.decode('utf8'))['data']['priceUsd']