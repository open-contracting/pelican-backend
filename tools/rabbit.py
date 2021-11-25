import simplejson as json
from yapw import clients

from tools import settings


def encode(message, content_type):
    return json.dumps(message).encode()


def decode(body, content_type):
    return json.loads(body.decode("utf-8"))


class Client(clients.Threaded, clients.Durable, clients.Blocking, clients.Base):
    pass


def create_client():
    return Client(url=settings.RABBIT_URL, exchange=settings.RABBIT_EXCHANGE_NAME, encode=encode, decode=decode)
