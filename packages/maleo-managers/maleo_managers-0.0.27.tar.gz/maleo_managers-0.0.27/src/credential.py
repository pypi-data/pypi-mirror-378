from Crypto.PublicKey.RSA import RsaKey
from datetime import datetime, timedelta, timezone
from google.oauth2.service_account import Credentials
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated
from uuid import UUID
from maleo.crypto.token import encode
from maleo.enums.environment import Environment
from maleo.google.secret import Format, GoogleSecretManager
from maleo.security.authentication import (
    SystemCredentials,
    AuthenticatedUser,
    SystemAuthentication,
)
from maleo.security.authorization import Scheme, Authorization
from maleo.security.token import Domain, SystemToken
from maleo.types.string import ListOfStrings
from maleo.types.uuid import OptionalUUID
from maleo.utils.loaders.yaml import from_string


class MaleoCredential(BaseModel):
    id: Annotated[int, Field(..., description="ID", ge=1)]
    uuid: Annotated[UUID, Field(..., description="UUID")]
    username: Annotated[str, Field(..., description="Username", max_length=50)]
    email: Annotated[str, Field(..., description="Email", max_length=255)]
    password: Annotated[str, Field(..., description="Password", max_length=255)]
    roles: Annotated[ListOfStrings, Field(..., description="Roles", min_length=1)]


class Credential(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    google: Credentials = Field(..., description="Google credentials")
    maleo: MaleoCredential = Field(..., description="Maleo credentials")


class CredentialManager:
    def __init__(
        self,
        environment: Environment,
        private_key: RsaKey,
        secret_manager: GoogleSecretManager,
        operation_id: OptionalUUID = None,
    ) -> None:
        self._private_key = private_key
        self._secret_manager = secret_manager

        name = f"maleo-internal-credentials-{environment}"
        read_secret = secret_manager.read(
            Format.STRING, name=name, operation_id=operation_id
        )
        data = from_string(read_secret.data.value)
        self.maleo_credentials = MaleoCredential.model_validate(data)

    def assign_google_credentials(self, google_credentials: Credentials) -> None:
        self.google_credentials = google_credentials

    @property
    def credential(self) -> Credential:
        if not hasattr(self, "google_credentials") or not isinstance(
            self.google_credentials, Credentials
        ):
            raise ValueError("Google credential not initialized")
        if not hasattr(self, "maleo_credentials") or not isinstance(
            self.maleo_credentials, MaleoCredential
        ):
            raise ValueError("Maleo credential not initialized")
        return Credential(google=self.google_credentials, maleo=self.maleo_credentials)

    @property
    def token(self) -> SystemToken:
        now = datetime.now(tz=timezone.utc)
        return SystemToken(
            iss=None,
            sub=self.maleo_credentials.uuid,
            aud=None,
            exp=int(now.timestamp()),
            iat=int((now + timedelta(minutes=15)).timestamp()),
            r=self.maleo_credentials.roles,
        )

    @property
    def token_str(self) -> str:
        return encode(self.token.model_dump(mode="json"), key=self._private_key)

    @property
    def authentication(self) -> SystemAuthentication:
        return SystemAuthentication(
            credentials=SystemCredentials(
                user_id=self.maleo_credentials.uuid,
                roles=self.maleo_credentials.roles,
                scopes=["authenticated"]
                + [f"{Domain.SYSTEM}:{role}" for role in self.maleo_credentials.roles],
            ),
            user=AuthenticatedUser(
                display_name=self.maleo_credentials.username,
                identity=self.maleo_credentials.email,
            ),
        )

    @property
    def authorizatiom(self) -> Authorization:
        return Authorization(scheme=Scheme.BEARER_TOKEN, credentials=self.token_str)
