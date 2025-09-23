# This file is placed in the Public Domain.


"brokers"


import time


class Fleet:

    clients = {}

    @staticmethod
    def add(client):
        if not client:
            return
        Fleet.clients[repr(client)] = client

    @staticmethod
    def all():
        return list(Fleet.clients.values())

    @staticmethod
    def announce(txt):
        for client in Fleet.all():
            client.announce(txt)

    @staticmethod
    def display(evt):
        client = Fleet.get(evt.orig)
        client.display(evt)

    @staticmethod
    def get(orig):
        return Fleet.clients.get(orig, None)

    @staticmethod
    def say(orig, channel, txt):
        client = Fleet.get(orig)
        client.say(channel, txt)

    @staticmethod
    def shutdown():
        for client in Fleet.all():
            client.stop()

    @staticmethod
    def wait():
        time.sleep(0.1)
        for client in Fleet.all():
            client.wait()


def __dir__():
    return (
        'Fleet',
   )
