import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from elasticsearch import AsyncElasticsearch, Elasticsearch
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from redis.asyncio import Redis as AsyncRedis
from redis import Redis as SyncRedis
from sqlalchemy import text
from typing import Generic, Type, TypeVar
from uuid import uuid4
from maleo.logging.enums import Level
from maleo.logging.logger import Database
from maleo.schemas.connection import OptionalConnectionContext
from maleo.schemas.error.enums import Code as ErrorCode
from maleo.schemas.exception.factory import Factory as MaleoExceptionFactory
from maleo.schemas.operation.context import generate
from maleo.schemas.operation.enums import (
    OperationType,
    SystemOperationType,
    Origin,
    Layer,
    Target,
)
from maleo.schemas.operation.mixins import Timestamp
from maleo.schemas.operation.system import (
    SystemOperationAction,
    SuccessfulSystemOperation,
)
from maleo.schemas.response import NoDataResponse
from maleo.schemas.service import ServiceContext, OptionalServiceContext
from maleo.security.authentication import OptionalAnyAuthentication
from maleo.security.authorization import OptionalAuthorization
from maleo.security.impersonation import OptionalImpersonation
from maleo.types.uuid import OptionalUUID
from ..config import (
    MySQLConfig,
    PostgreSQLConfig,
    SQLiteConfig,
    SQLServerConfig,
    SQLConfigT,
    ElasticsearchConfig,
    MongoConfig,
    RedisConfig,
    NoSQLConfigT,
    ConfigT,
)
from ..enums import Connection
from ..types import DeclarativeBaseT
from .client import (
    AsyncClientT,
    SyncClientT,
    ClientManager,
)
from .engine import EngineManager
from .session import SessionManager


class Manager(ABC, Generic[ConfigT]):
    def __init__(
        self,
        config: ConfigT,
        logger: Database,
        service_context: OptionalServiceContext = None,
    ) -> None:
        super().__init__()
        self._config = config
        self._logger = logger
        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )
        self._operation_context = generate(
            origin=Origin.SERVICE,
            layer=Layer.UTILITY,
            target=Target.DATABASE,
        )

    @abstractmethod
    async def async_check_connection(
        self,
        operation_id: OptionalUUID = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAuthorization = None,
        impersonation: OptionalImpersonation = None,
    ) -> bool:
        pass

    @abstractmethod
    def sync_check_connection(
        self,
        operation_id: OptionalUUID = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAuthorization = None,
        impersonation: OptionalImpersonation = None,
    ) -> bool:
        pass

    @abstractmethod
    async def dispose(self):
        pass


class SQLManager(Manager[SQLConfigT], Generic[SQLConfigT, DeclarativeBaseT]):
    def __init__(
        self,
        Base: Type[DeclarativeBaseT],
        config: SQLConfigT,
        logger: Database,
        service_context: OptionalServiceContext = None,
    ) -> None:
        super().__init__(config, logger, service_context)
        self._operation_context.target.details = self._config.model_dump()
        self._engine_manager = EngineManager[SQLConfigT](config)
        self._session_manager = SessionManager(
            config=config,
            engines=self._engine_manager.get_all(),
            logger=self._logger,
            service_context=self._service_context,
        )
        self.Base = Base
        self.Base.metadata.create_all(bind=self._engine_manager.get(Connection.SYNC))

    @property
    def engine(self) -> EngineManager[SQLConfigT]:
        return self._engine_manager

    @property
    def session(self) -> SessionManager:
        return self._session_manager

    async def async_check_connection(
        self,
        operation_id: OptionalUUID = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAuthorization = None,
        impersonation: OptionalImpersonation = None,
    ) -> bool:
        """Check database connectivity by executing a simple query."""
        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = SystemOperationAction(
            type=SystemOperationType.DATABASE_CONNECTION, details=None
        )
        executed_at = datetime.now(tz=timezone.utc)
        try:
            async with self._session_manager.get(
                Connection.ASYNC,
                operation_id=operation_id,
                connection_context=connection_context,
                authentication=authentication,
                authorization=authorization,
                impersonation=impersonation,
            ) as session:
                await session.execute(text("SELECT 1"))
                SuccessfulSystemOperation[
                    OptionalAnyAuthentication,
                    OptionalAuthorization,
                    NoDataResponse[None],
                ](
                    service_context=self._service_context,
                    id=operation_id,
                    context=self._operation_context,
                    action=operation_action,
                    timestamp=Timestamp.completed_now(executed_at),
                    summary="Database connectivity check successful",
                    connection_context=connection_context,
                    authentication=authentication,
                    authorization=authorization,
                    impersonation=impersonation,
                    response=NoDataResponse[None](metadata=None, other=None),
                ).log(
                    self._logger, Level.INFO
                )
            return True
        except Exception as e:
            exc = MaleoExceptionFactory[
                OptionalAnyAuthentication, OptionalAuthorization
            ].from_code(
                ErrorCode.INTERNAL_SERVER_ERROR,
                details={
                    "exc_type": type(e).__name__,
                    "exc_data": {
                        "message": str(e),
                        "args": e.args,
                    },
                },
                operation_type=OperationType.SYSTEM,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_action=operation_action,
                operation_timestamp=Timestamp.completed_now(executed_at),
                operation_summary="Unexpected error occured checking database connection asynchronously",
                connection_context=connection_context,
                authentication=authentication,
                authorization=authorization,
                impersonation=impersonation,
            )
            exc.operation.log(self._logger, level=Level.ERROR)
            return False

    def sync_check_connection(
        self,
        operation_id: OptionalUUID = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAuthorization = None,
        impersonation: OptionalImpersonation = None,
    ) -> bool:
        """Check database connectivity by executing a simple query."""
        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = SystemOperationAction(
            type=SystemOperationType.DATABASE_CONNECTION, details=None
        )
        executed_at = datetime.now(tz=timezone.utc)
        try:
            with self._session_manager.get(
                Connection.SYNC,
                operation_id=operation_id,
                connection_context=connection_context,
                authentication=authentication,
                authorization=authorization,
                impersonation=impersonation,
            ) as session:
                session.execute(text("SELECT 1"))
                SuccessfulSystemOperation[
                    OptionalAnyAuthentication,
                    OptionalAuthorization,
                    NoDataResponse[None],
                ](
                    service_context=self._service_context,
                    id=operation_id,
                    context=self._operation_context,
                    action=operation_action,
                    timestamp=Timestamp.completed_now(executed_at),
                    summary="Database connectivity check successful",
                    connection_context=connection_context,
                    authentication=authentication,
                    authorization=authorization,
                    impersonation=impersonation,
                    response=NoDataResponse[None](metadata=None, other=None),
                ).log(
                    self._logger, Level.INFO
                )
            return True
        except Exception as e:
            exc = MaleoExceptionFactory[
                OptionalAnyAuthentication, OptionalAuthorization
            ].from_code(
                ErrorCode.INTERNAL_SERVER_ERROR,
                details={
                    "exc_type": type(e).__name__,
                    "exc_data": {
                        "message": str(e),
                        "args": e.args,
                    },
                },
                operation_type=OperationType.SYSTEM,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_action=operation_action,
                operation_timestamp=Timestamp.completed_now(executed_at),
                operation_summary="Unexpected error occured checking database connection synchronously",
                connection_context=connection_context,
                authentication=authentication,
                authorization=authorization,
                impersonation=impersonation,
            )
            exc.operation.log(self._logger, level=Level.ERROR)
            return False

    async def dispose(self):
        self._session_manager.dispose()
        await self._engine_manager.dispose()


class MySQLManager(
    SQLManager[MySQLConfig, DeclarativeBaseT], Generic[DeclarativeBaseT]
):
    pass


class PostgreSQLManager(
    SQLManager[PostgreSQLConfig, DeclarativeBaseT], Generic[DeclarativeBaseT]
):
    pass


class SQLiteManager(
    SQLManager[SQLiteConfig, DeclarativeBaseT], Generic[DeclarativeBaseT]
):
    pass


class SQLServerManager(
    SQLManager[SQLServerConfig, DeclarativeBaseT], Generic[DeclarativeBaseT]
):
    pass


SQLManagerT = TypeVar(
    "SQLManagerT",
    MySQLManager,
    PostgreSQLManager,
    SQLiteManager,
    SQLServerManager,
)


class NoSQLManager(
    Manager[NoSQLConfigT],
    Generic[
        NoSQLConfigT,
        AsyncClientT,
        SyncClientT,
    ],
):
    def __init__(
        self,
        config: NoSQLConfigT,
        logger: Database,
        service_context: OptionalServiceContext = None,
    ) -> None:
        super().__init__(config, logger, service_context)
        self._operation_context.target.details = self._config.model_dump()
        self._client_manager = ClientManager[
            NoSQLConfigT,
            AsyncClientT,
            SyncClientT,
        ](config)

    @property
    def client(self) -> ClientManager[
        NoSQLConfigT,
        AsyncClientT,
        SyncClientT,
    ]:
        return self._client_manager

    async def async_check_connection(
        self,
        operation_id: OptionalUUID = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAuthorization = None,
        impersonation: OptionalImpersonation = None,
    ) -> bool:
        """Check client connectivity by executing a simple query."""
        client = self._client_manager.get(Connection.ASYNC)
        try:
            if isinstance(client, AsyncElasticsearch):
                return await client.ping()
            elif isinstance(client, AsyncIOMotorClient):
                db = client.get_database(str(self._config.connection.database))
                await db.command("ping")
                return True
            elif isinstance(client, AsyncRedis):
                await client.ping()
                return True
            else:
                raise TypeError(f"Invalid client type: '{type(client)}'")
        except Exception:
            print("Unable to check client connection:\n", traceback.format_exc())
            return False

    def sync_check_connection(
        self,
        operation_id: OptionalUUID = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAuthorization = None,
        impersonation: OptionalImpersonation = None,
    ) -> bool:
        """Check client connectivity by executing a simple query."""
        client = self._client_manager.get(Connection.SYNC)
        try:
            if isinstance(client, Elasticsearch):
                return client.ping()
            elif isinstance(client, MongoClient):
                db = client.get_database(str(self._config.connection.database))
                db.command("ping")
                return True
            elif isinstance(client, SyncRedis):
                client.ping()
                return True
            else:
                raise TypeError(f"Invalid client type: '{type(client)}'")
        except Exception:
            print("Unable to check client connection:\n", traceback.format_exc())
            return False

    async def dispose(self):
        await self._client_manager.dispose()


class ElasticsearchManager(
    NoSQLManager[ElasticsearchConfig, AsyncElasticsearch, Elasticsearch]
):
    pass


class MongoManager(NoSQLManager[MongoConfig, AsyncIOMotorClient, MongoClient]):
    pass


class RedisManager(NoSQLManager[RedisConfig, AsyncRedis, SyncRedis]):
    pass


NoSQLManagerT = TypeVar(
    "NoSQLManagerT",
    ElasticsearchManager,
    MongoManager,
    RedisManager,
)


ManagerT = TypeVar(
    "ManagerT",
    ElasticsearchManager,
    MongoManager,
    RedisManager,
    MySQLManager,
    PostgreSQLManager,
    SQLiteManager,
    SQLServerManager,
)
