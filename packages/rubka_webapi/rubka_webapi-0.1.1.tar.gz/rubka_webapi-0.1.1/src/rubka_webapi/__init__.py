
from .client.client import Client
from .types.models import Message, User, Chat, AuthData
from .exceptions import RubkaWebAPIException, NetworkError, AuthError, APIError, InvalidSessionError

__version__ = "0.1.0"
__author__ = "httex"

# You can also define a convenient run function here if needed
# async def run_client(...):
#    client = Client(...)
#    await client.run()

