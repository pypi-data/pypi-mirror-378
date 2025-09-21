import logging
from typing import TYPE_CHECKING, Any

from socketio import AsyncNamespace

if TYPE_CHECKING:
    from socketio import AsyncServer
    from sqlalchemy.ext.asyncio import async_sessionmaker


logger = logging.getLogger(__name__)


class BaseSocketHandler(AsyncNamespace):

    def __init__(
        self,
        sio: "AsyncServer",
        session_factory: "async_sessionmaker",
        namespace: str = "/",
        **services: Any,
    ):
        self.sio = sio
        self.session_factory = session_factory
        self.services = services
        super().__init__(namespace)
