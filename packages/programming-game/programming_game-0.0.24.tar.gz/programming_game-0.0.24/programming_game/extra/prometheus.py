import asyncio
import functools
from contextlib import asynccontextmanager

from loguru import logger

from programming_game.protocol import ClientProtocol
from programming_game.schema.messages import EventsMessage

try:
    from aioprometheus import Counter
    from aioprometheus.service import Service

    _prometheus_available = True
except ModuleNotFoundError:
    _prometheus_available = False

logger.warning("Prometheus {}", _prometheus_available)


@asynccontextmanager
async def setup_prometheus(client: "PrometheusMixin"):
    service = Service()
    await service.start(addr="0.0.0.0", port=9000)
    logger.info("Setting up prometheus client. {}", service.metrics_url)
    try:
        yield
    finally:
        service.stop()
        logger.info("Shutting down prometheus client.")
    pass


if _prometheus_available:

    class PrometheusMixin(ClientProtocol):
        def __init__(self, **kwargs):
            self.context_managers.append(setup_prometheus(self))
            super().__init__(**kwargs)

        @staticmethod
        def prom_count_events(func):
            events_counter = Counter("events_total", "Number of incoming events")

            def decorator(client, message, *args, **kwargs):
                if type(message) is EventsMessage:
                    for instance_id, instance_events in message.value.items():
                        for char_id, char_events in instance_events.items():
                            for event in char_events:
                                events_counter.inc(
                                    {
                                        "kind": event.__struct_config__.tag,
                                        "instance": instance_id,
                                        "character": char_id,
                                    }
                                )
                return func(client, message, *args, **kwargs)

            return decorator

        @staticmethod
        def prom_count_calls(counter_name: str, help_text: str = ""):
            counter = Counter(counter_name, help_text)

            def decorator(func):
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    counter.inc({"function": func.__name__})
                    return func(*args, **kwargs)

                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    counter.inc({"function": func.__name__})
                    return await func(*args, **kwargs)

                if asyncio.iscoroutinefunction(func):
                    return async_wrapper
                else:
                    return sync_wrapper

            return decorator
else:

    class PrometheusMixin(ClientProtocol):
        @staticmethod
        def prom_count_calls(counter_name: str, help_text: str = ""):
            def decorator(func):
                return func

            return decorator

        @staticmethod
        def prom_count_events(func):
            def decorator(*args, **kwargs):
                return func(*args, **kwargs)

            return decorator
