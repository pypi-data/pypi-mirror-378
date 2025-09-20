#  Copyright (c) Kuba Szczodrzyński 2023-1-9.

from logging import debug, exception
from threading import Event, Thread
from typing import Callable


class BaseThread(Thread):
    _stop_flag: Event
    on_stop: Callable[["BaseThread"], None] = None

    def __init__(self):
        super().__init__()
        self._stop_flag = Event()

    def run_impl(self):
        pass

    def run(self):
        debug(f"Started {type(self).__name__}")
        self._stop_flag.clear()

        try:
            self.run_impl()
        except Exception as e:
            if self.should_run():
                # show exceptions only if not cancelled
                exception("An error has occurred", exc_info=e)
            self.stop()

        if self.on_stop:
            self.on_stop(self)
        debug(f"Stopped {type(self).__name__}")

    def stop(self):
        self._stop_flag.set()

    def should_run(self) -> bool:
        return not self._stop_flag.is_set()

    def should_stop(self) -> bool:
        return self._stop_flag.is_set()
