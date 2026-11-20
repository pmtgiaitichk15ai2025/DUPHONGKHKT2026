"""Share completed audio and one in-flight synthesis per exact cache key."""
from concurrent.futures import Future
from threading import Lock


class AudioCache:
    def __init__(self, completed, max_entries):
        self.completed = completed
        self.max_entries = max_entries
        self._pending = {}
        self._lock = Lock()

    def get_or_create(self, key, produce):
        with self._lock:
            if key in self.completed:
                return self.completed[key]
            pending = self._pending.get(key)
            owner = pending is None
            if owner:
                pending = self._pending[key] = Future()
        if not owner:
            return pending.result()
        try:
            result = produce()
            with self._lock:
                if result:
                    while len(self.completed) >= self.max_entries:
                        self.completed.pop(next(iter(self.completed)))
                    self.completed[key] = result
            pending.set_result(result)
            return result
        except BaseException as exc:
            pending.set_exception(exc)
            raise
        finally:
            with self._lock:
                self._pending.pop(key, None)
