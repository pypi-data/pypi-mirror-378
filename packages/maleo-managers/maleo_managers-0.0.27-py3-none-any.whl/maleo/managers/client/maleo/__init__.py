from abc import ABC, abstractmethod
from Crypto.PublicKey.RSA import RsaKey
from maleo.database.handlers import RedisHandler
from maleo.logging.config import Config as LogConfig
from maleo.logging.logger import Client
from maleo.schemas.operation.context import generate
from maleo.schemas.service import ServiceContext, OptionalServiceContext
from maleo.database.enums import CacheOrigin, CacheLayer
from maleo.schemas.operation.enums import Origin, Layer, Target
from ...credential import CredentialManager
from ..http import HTTPClientManager
from .config import MaleoClientConfig


class MaleoClientService:
    def __init__(
        self,
        *,
        config: MaleoClientConfig,
        logger: Client,
        credential_manager: CredentialManager,
        http_client_manager: HTTPClientManager,
        private_key: RsaKey,
        redis: RedisHandler,
        service_context: ServiceContext,
    ):
        self._config = config
        self._logger = logger
        self._credential_manager = credential_manager
        self._http_client_manager = http_client_manager
        self._private_key = private_key
        self._redis = redis
        self._service_context = service_context

        self._namespace = self._redis.config.additional.build_namespace(
            use_self_base=True,
            client=self._config.key,
            origin=CacheOrigin.CLIENT,
            layer=CacheLayer.SERVICE,
        )

        self._operation_context = generate(
            origin=Origin.CLIENT, layer=Layer.SERVICE, target=Target.INTERNAL
        )


class MaleoClientManager(ABC):
    def __init__(
        self,
        *,
        config: MaleoClientConfig,
        log_config: LogConfig,
        credential_manager: CredentialManager,
        private_key: RsaKey,
        redis: RedisHandler,
        service_context: OptionalServiceContext = None,
    ):
        self._config = config
        self._log_config = log_config

        self._key = self._config.key
        self._name = self._config.name

        self._logger = Client(
            environment=self._service_context.environment,
            service_key=self._service_context.key,
            client_key=self._key,
            config=log_config,
        )

        self._credential_manager = credential_manager
        self._http_client_manager = HTTPClientManager()
        self._private_key = private_key
        self._redis = redis

        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )

    @abstractmethod
    def initalize_services(self):
        pass
