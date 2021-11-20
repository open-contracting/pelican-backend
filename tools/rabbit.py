import simplejson as json
from yapw import clients

from tools import settings


def encoder(message):
    json.dumps(message).encode()


class Client(clients.Threaded, clients.Durable, clients.Blocking, clients.Base):
    pass


def create_client():
    return Client(url=settings.RABBIT_URL, exchange=settings.RABBIT_EXCHANGE_NAME, encoder=encoder)
