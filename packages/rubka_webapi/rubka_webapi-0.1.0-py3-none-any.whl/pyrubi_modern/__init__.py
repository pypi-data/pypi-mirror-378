
from .client.client import Client
from .types.models import Message, User, Chat, AuthData
from .exceptions import PyrubiException, NetworkError, AuthError, APIError, InvalidSessionError

__version__ = "0.1.0"
__author__ = "Manus AI"

# You can also define a convenient run function here if needed
# async def run_client(...):
#    client = Client(...)
#    await client.run()

