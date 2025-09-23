import ssl
import sys
from urllib3 import poolmanager
from requests.adapters import HTTPAdapter
import requests


class SSLAdapter(HTTPAdapter):
    """
    An HTTPS Transport Adapter that enables SSL connections
    """

    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        if sys.version_info >= (3, 12):
            context.options |= ssl.OP_LEGACY_SERVER_CONNECT
        kwargs["ssl_context"] = context
        return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)


class SingletonSession:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = requests.Session()
            cls._instance.mount("https://", SSLAdapter())
        return cls._instance
