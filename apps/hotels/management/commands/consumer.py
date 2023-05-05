import json
import logging
import os

from django.core.management import BaseCommand
from kafka import KafkaConsumer

from apps.hotels.models import Hotel


logger = logging.getLogger('django')


class Command(BaseCommand):
    help = 'Start kafka consumer to listen "hotels" app events'

    def handle(self, *args, **options):
        kafka_url = os.environ.get('KAFKA_URL', 'localhost:9092')
        logger.info(f'KAFKA_URL: {kafka_url}')
        try:
            consumer = KafkaConsumer(
                bootstrap_servers=kafka_url,
                # security_protocol="SSL",
                # ssl_cafile="./ca.pem",
                # ssl_certfile="./service.cert",
                # ssl_keyfile="./service.key",
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset='earliest'
            )
            logger.info('Consumer started')
        except Exception as e:
            logger.error('Consumer failed to start')
            raise e

        topic = os.environ.get('KAFKA_TOPIC', 'demo')
        consumer.subscribe(topics=[topic])
        logger.info(f'Consumer subscribed to "{topic}" topic')

        for message in consumer:
            logger.info(f'Consumer received message: {message.value}')
            if message.value:
                hotels = [Hotel(**i) for i in message.value]
                objs = Hotel.objects.bulk_create(hotels, ignore_conflicts=True)
                print(f'{len(objs)} created')
                logger.info(f'{len(objs)} Hotel objects stored')
