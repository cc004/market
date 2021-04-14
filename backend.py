class backend:
    def __getitem__(self, indices) -> int:
        raise NotImplementedError
    def __setitem__(self, indices, value: int):
        raise NotImplementedError


class duel_backend(backend):
    def __init__(self):
        from hoshino.modules.pcrduel.ScoreCounter import ScoreCounter2
        self.sc = ScoreCounter2()
    
    def __getitem__(self, indices):
        return self.sc._get_score(indices[0], indices[1])
    
    def __setitem__(self, indices, value):
        self.sc._add_score(indices[0], indices[1], value - self.__getitem__(indices))

from .utils import config

class json_backend(backend):
    def __init__(self):
        self.config = config('money.json')

    def _ensure(self, gid, uid):
        if gid not in self.config.json:
            self.config.json[gid] = {}
        if uid not in self.config.json[gid]:
            self.config.json[gid][uid] = 1000

    def __getitem__(self, indices):
        gid, uid = indices
        self._ensure(gid, uid)
        return self.config.json[gid][uid]
    def __setitem__(self, indices, value):
        gid, uid = indices
        self._ensure(gid, uid)
        self.config.json[gid][uid] = value
        self.config.save()

class balance:
    def __init__(self):
        self.config = config('balance.json')

    def _ensure(self, gid, uid, item = None):
        if gid not in self.config.json:
            self.config.json[gid] = {}
        if uid not in self.config.json[gid]:
            self.config.json[gid][uid] = {}
        if item and item not in self.config.json[gid][uid]:
            self.config.json[gid][uid][item] = 0

    def __getitem__(self, indices):
        if len(indices) == 2: # XXX: DO NOT MODIFY ITEMS IN THIS WAY
            gid, uid = indices
            self._ensure(gid, uid)
            return self.config.json[gid][uid]
        else:
            gid, uid, item = indices
            self._ensure(gid, uid, item)
            return self.config.json[gid][uid][item]
    
    def __setitem__(self, indices, value):
        gid, uid, item = indices
        self._ensure(gid, uid, item)
        self.config.json[gid][uid][item] = value
        self.config.save()
