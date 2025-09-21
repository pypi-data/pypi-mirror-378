import time
from collections.abc import Awaitable, Callable
from typing import Any

from loguru import logger

from programming_game.structure.on_tick_response import OnTickResponse, TickPause
from programming_game.tasks.task_meta import TaskMeta


class Task(metaclass=TaskMeta):
    _sub_task: "Task | None" = None

    @staticmethod
    def on_tick(
        *,
        interval: float | None = None,
        run_before_subtask: bool = False,
    ) -> Callable[[Callable], Callable]:
        """
        Ein parametrisierter Decorator zum Markieren einer asynchronen on_tick-Methode.

        wenn true zurückgegeben wird, wird der aktuelle task beendet (sub-task)
        kann einen task zurüggeben der dann als subtask gesetzt wird

        Reihenfolge:
            - before_handler
            - [subtask]
            ( Ende falls subtask noch aktiv )
            - [on_event handler]
            - normal_handler

        Parameter:
            interval: der befehl wird erst nach x sekunden erneut aufgerufen (nicht bei after_handlers)
            run_before_subtask: Führe diese Methode immer aus, auch wenn ein subtask gesetzt ist. läuft daher immer vor on_event-Handler.
        """

        def decorator(
            func: Callable[[Any], Awaitable[OnTickResponse]],
        ) -> Callable[[Any], Awaitable[OnTickResponse]]:
            """Der eigentliche Decorator, der die Funktion umhüllt."""
            func._on_tick_method = True
            func._interval = interval
            func._last_run = 0.0
            func._run_before_subtask = run_before_subtask
            return func

        return decorator

    @staticmethod
    def on_event(event_filter: Any = None) -> Callable[[Callable], Callable]:
        """
        Ein Decorator zum Markieren einer asynchronen on_event-Methode.
        Diese Methode wird aufgerufen, wenn Events vorhanden sind, bevor on_tick-Methoden ausgeführt werden.

        Parameter:
            event_filter: Optional filter für Events (z.B. MovedEvent oder (MovedEvent, CaloriesEvent)).
                          Wenn None, wird die Methode für alle Events aufgerufen.
        """

        def decorator(
            func: Callable[[Any, Any], Awaitable[None]],
        ) -> Callable[[Any, Any], Awaitable[None]]:
            """Der eigentliche Decorator, der die Funktion umhüllt."""
            func._on_event_method = True
            func._event_filter = event_filter
            return func

        return decorator

    async def _handle_return(self, result):
        if isinstance(result, Task):
            self._sub_task = result
            return TickPause(0.005)
        return result

    async def __call__(self, *, game_state, events, **kwargs):
        start = time.time()
        self.gs = game_state
        self.events = events

        # Sammle Handler basierend auf ihren Flags
        before_handlers = [
            h for h in self._on_tick_method
            if getattr(h, "_run_before_subtask", False)
        ]
        normal_handlers = [
            h for h in self._on_tick_method
            if not getattr(h, "_run_before_subtask", False) and not getattr(h, "_run_after_subtask", False)
        ]

        # Führe before_handlers aus (vor Subtask)
        for handler in before_handlers:
            interval = getattr(handler, "_interval", None)
            if interval is not None and start - handler._last_run < interval:
                continue
            handler._last_run = start
            if result := await self._handle_return(await handler(self)):
                return result

        if self._sub_task:
            subtask_result = await self._sub_task(game_state=game_state, events=events, **kwargs)
            if subtask_result is True:
                logger.debug("Subtask finished", self._sub_task)
                self._sub_task = None
            elif subtask_result:
                return subtask_result

        if self._on_event_method:
            for handler, event_filter in self._on_event_method:
                if event_filter is None:
                    await handler(self, events)
                else:
                    filtered_events = [event for event in events if isinstance(event, event_filter)]
                    if filtered_events:
                        await handler(self, filtered_events)

        # Führe normal_handlers aus (nach Subtask-Logik)
        for handler in normal_handlers:
            interval = getattr(handler, "_interval", None)
            if interval is not None and start - handler._last_run < interval:
                continue
            handler._last_run = start
            if result := await self._handle_return(await handler(self)):
                return result

        return None

    def set_subtask(self, param):
        self._sub_task = param
        logger.debug("New Subtask {}", type(self._sub_task))

    @property
    def player(self):
        return self.gs.player

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.player.name})>"
