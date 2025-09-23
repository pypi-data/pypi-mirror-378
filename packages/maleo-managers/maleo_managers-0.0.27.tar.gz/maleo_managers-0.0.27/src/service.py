from abc import ABC, abstractmethod
from google.cloud import pubsub_v1
from typing import Generic
from maleo.schemas.settings import ServiceSettingsT
from maleo.logging.config import Config as LogConfig
from maleo.logging.logger import ServiceLoggers
from .config import ConfigT


class ServiceManager(ABC, Generic[ServiceSettingsT, ConfigT]):
    """ServiceManager class"""

    def __init__(self, log_config: LogConfig, settings: ServiceSettingsT):
        self._log_config = log_config
        self._settings = settings

        self._initialize_loggers()
        self._initialize_publisher()

    def _initialize_loggers(self) -> None:
        self.loggers = ServiceLoggers.new(
            environment=self._settings.ENVIRONMENT,
            service_key=self._settings.SERVICE_KEY,
            config=self._log_config,
        )

    def _initialize_publisher(self) -> None:
        self.publisher = pubsub_v1.PublisherClient()

    @abstractmethod
    def _initialize_database(self):
        """Initialize all given databases"""

    @abstractmethod
    def _initialize_google_cloud_storage(self):
        """Initialize Google Cloud Storage"""
