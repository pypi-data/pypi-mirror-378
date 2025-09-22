from confluent_kafka import Producer, Consumer
import json
import logging


class KafkaProducer():
    def __init__(self, config: dict = {}):
        aux_config = {
            'bootstrap.servers': 'localhost:9092',
            'linger.ms': 10,
            'retries': 4,
        }

        for key in config:
            aux_config[key] = config[key]

        self.producer = Producer(aux_config)

    def _delivery_report(self, err, msg):
        if err is not None:
            logging.error(f"[Kafka] Sending msg failed: {err}")
        else:
            logging.info(
                f"[Kafka] Msg sent to topic {msg.topic()}, partition {msg.partition()}")

    def send(self, topic: str, key: str, value: dict) -> None:
        self.producer.produce(
            topic=topic,
            key=key.encode("utf-8"),
            value=json.dumps(value).encode("utf-8"),
            callback=self._delivery_report
        )
        self.producer.poll(0)
        self.producer.flush()

    def close(self) -> None:
        self.producer.close()


class KafkaConsumer():
    def __init__(self, config: dict = {}):
        aux_config = {
            "bootstrap.servers": "localhost:9092",
            "group.id": "default-consumer-group",
            "auto.offset.reset": "earliest",
        }

        for key in config:
            aux_config[key] = config[key]

        self.consumer = Consumer(aux_config)

    def start_receiving(self, topic: str) -> None:
        try:
            self.consumer.subscribe([topic])
            logging.info(f"[Kafka] Listening messages from topic: {topic}")
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue

                err = msg.error()
                if err:
                    logging.error(f"[Kafka] One msg reception failed: {err}")
                    continue

                data = json.loads(msg.value().decode("utf-8"))
                logging.info(f"Msg received: {data}")
        except KeyboardInterrupt:
            logging.info("[Kafka] Listening stopped mannualy.")
        finally:
            self.consumer.close()
