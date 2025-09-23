import abc
from typing import AsyncIterable, AsyncIterator

from .values import DeviceKey, Event, Message, MQTTMessage, Payload


class SessionIsBroken(Exception):
    """MessageSession has broken accidentallly"""


class MessageSession(abc.ABC):
    """Interface to manage messages, plain msgs are the only value objects it manages"""

    @abc.abstractmethod
    async def establish(self):
        ...

    @abc.abstractmethod
    async def terminate(self):
        ...

    @abc.abstractmethod
    def is_established(self) -> bool:
        ...

    @abc.abstractmethod
    async def subscribe(self) -> AsyncIterable[Message]:
        yield Message(Event.NODE_HAS_DIED, DeviceKey(""))

    @abc.abstractmethod
    async def publish(self, msg: Message):
        ...


class MQTTError(Exception):
    """Connection error to MQTT Broker, it implies session is terminated"""

    def __init__(self, wrapped: Exception):
        self.wrapped = wrapped
        super().__init__(str(wrapped))


class MQTT5Client(abc.ABC):
    """Interface to publish messages to MQTT"""

    @abc.abstractmethod
    async def connect(self, will: MQTTMessage):
        ...

    @abc.abstractmethod
    async def publish(self, message: MQTTMessage):
        ...

    @abc.abstractmethod
    async def disconnect(self):
        ...

    @abc.abstractmethod
    async def subscribe(self, wildcard: str, qos: int):
        ...

    @abc.abstractmethod
    async def unsubscribe(self, wildcard: str):
        ...

    @property
    @abc.abstractmethod
    def messages(self) -> AsyncIterator[MQTTMessage]:
        ...


class EncodingError(Exception):
    """Failure when encoding/decoding the payload of MQTTMessage"""


class PayloadEncoder(abc.ABC):
    """Encode the message before sending it as payload in the message"""

    @abc.abstractmethod
    def encode(self, payload: Payload) -> bytes:
        """Convert a payload to a sequence of bytes"""
        ...

    @abc.abstractmethod
    def decode(self, b: bytes) -> Payload:
        """Convert bytes to a payload class"""
