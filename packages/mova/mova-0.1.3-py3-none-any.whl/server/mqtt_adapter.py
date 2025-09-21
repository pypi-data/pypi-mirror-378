#!/usr/bin/env python3

"""Adapter MQTT dla serwera Mova - obsługa publikowania i subskrybowania wiadomości."""

import os
import json
import logging
import asyncio
from asyncio_mqtt import Client, MqttError

logger = logging.getLogger("mova.mqtt_adapter")

class MQTTAdapter:
    def __init__(self, config):
        self.broker = config.get('mqtt', {}).get('broker', 'localhost')
        self.port = config.get('mqtt', {}).get('port', 1883)
        self.topic = config.get('mqtt', {}).get('topic', 'logs/test')
        self.enabled = config.get('mqtt', {}).get('enabled', False)
        self.client = None

    async def connect(self):
        if not self.enabled:
            logger.warning("MQTT jest wyłączony w konfiguracji.")
            return False
        try:
            self.client = Client(self.broker, port=self.port)
            await self.client.connect()
            logger.info(f"Połączono z brokerem MQTT: {self.broker}:{self.port}")
            return True
        except MqttError as e:
            logger.error(f"Błąd połączenia z MQTT: {e}")
            return False

    async def publish(self, topic=None, message=None):
        if not self.enabled or not self.client:
            logger.warning("MQTT jest wyłączony lub nie połączono.")
            return False
        try:
            topic = topic or self.topic
            if isinstance(message, dict):
                message = json.dumps(message)
            await self.client.publish(topic, message)
            logger.info(f"Opublikowano wiadomość na temat {topic}: {message}")
            return True
        except MqttError as e:
            logger.error(f"Błąd publikacji MQTT: {e}")
            return False

    async def subscribe(self, topic=None, callback=None):
        if not self.enabled or not self.client:
            logger.warning("MQTT jest wyłączony lub nie połączono.")
            return False
        try:
            topic = topic or self.topic
            await self.client.subscribe(topic)
            logger.info(f"Zasubskrybowano temat: {topic}")
            async with self.client.unfiltered_messages() as messages:
                async for msg in messages:
                    payload = msg.payload.decode()
                    logger.info(f"Otrzymano wiadomość z tematu {msg.topic}: {payload}")
                    if callback:
                        await callback(msg.topic, payload)
        except MqttError as e:
            logger.error(f"Błąd subskrypcji MQTT: {e}")
            return False

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()
            logger.info("Rozłączono z brokerem MQTT.")

if __name__ == '__main__':
    # Test adaptera
    config = {'mqtt': {'enabled': False, 'broker': 'localhost', 'port': 1883, 'topic': 'test/topic'}}
    adapter = MQTTAdapter(config)
    logger.info("Test adaptera MQTT - w trybie wyłączonym nie połączy się.")
