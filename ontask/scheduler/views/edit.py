# -*- coding: utf-8 -*-

"""Factory to edit scheduled objects"""

class ScheduledOperationEditFactory(object):
    """Factory class to edit scheduled operations"""

    def __init__(self):
        self._builders = {}

    def register_builder(self, key, builder):
        self._builders[key] = builder

    def edit(self, key, **kwargs):
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)

class ActionPersonalizedTextService:
    """Process the personalizedText"""
    def __init__(self, payload):
        self._payload = payload

    def test_connection(self):
        print(f'Payload is {self._payload}')

class ActionPersonalizedTextServiceBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, payload, **_ignored):
        if not self._instance:
            self._instance = ActionPersonalizedTextService(payload)
        return self._instance

    def authorize(self, key, secret):
        return 'SPOTIFY_ACCESS_CODE'

factory = ScheduledOperationEditFactory()
factory.register()

