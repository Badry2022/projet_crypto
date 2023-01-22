from kafka import KafkaProducer
import asyncio
from project.binance import Kline
import json

kafka_producer = KafkaProducer(bootstrap_servers="192.168.1.59")
kline_btceur_1s = Kline("BTCEUR")

async def main():
    def handle_socket_message(msg):
        json_msg = json.loads(msg)
        kafka_producer.send(
            topic="BTCEUR-1s",
            value=json.dumps(json_msg).encode("utf-8")
        )

    kline_btceur_1s.subscribe_socket(handle_socket_message)
    while True:
        await asyncio.sleep(0.0001)

asyncio.run(main())
