from confluent_kafka import Producer, Consumer, Message, KafkaError
from typing import Callable, Optional, Union

PRODUCER_DEFAULT_CONFIG = {
    'bootstrap.servers': 'localhost:9092',
}

CONSUMER_DEFAULT_CONFIG = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "default_group_id",
}


class KafkaProducer():
    def __init__(self, config: dict = {}):
        for key, value in PRODUCER_DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value

        self.producer = Producer(config)

    def send(self,
             topic: str,
             partition: Optional[int] = None,
             key: Optional[Union[str, bytes]] = None,
             headers: Optional[Union[dict, list]] = None,
             value: Optional[Union[str, bytes]] = None,
             delivery_report_handler: Optional[Callable[[
                 KafkaError, Message], None]] = None
             ) -> None:

        kwargs = {"topic": topic}

        if partition is not None:
            kwargs["partition"] = partition
        if key is not None:
            kwargs["key"] = key
        if value is not None:
            kwargs["value"] = value
        if headers is not None:
            kwargs["headers"] = headers
        if delivery_report_handler is not None:
            kwargs["callback"] = delivery_report_handler

        self.producer.produce(**kwargs)
        self.producer.poll(0)
        self.producer.flush()


class KafkaConsumer():
    def __init__(self, config: dict = {}):
        for key, value in CONSUMER_DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value

        self.consumer = Consumer(config)

    def receive(self,
                topics: list[str],
                block_timeout: Optional[float] = None
                ) -> Union[Message, None]:
        self.consumer.subscribe(topics)

        if block_timeout is not None:
            return self.consumer.poll(timeout=block_timeout)
        else:
            return self.consumer.poll()

    def receive_loop(self,
                     topics: list[str],
                     msg_handler: Callable[[Message], None],
                     error_handler: Optional[Callable[[Message], None]] = None
                     ) -> None:
        try:
            self.consumer.subscribe(topics)
            while True:
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    if error_handler:
                        error_handler(msg)
                    continue

                msg_handler(msg)
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.unsubscribe()

    def close(self) -> None:
        self.consumer.close()


class KafkaConnector(KafkaProducer, KafkaConsumer):
    def __init__(self, producer_config, consumer_config):
        KafkaProducer.__init__(self, producer_config)
        KafkaConsumer.__init__(self, consumer_config)
