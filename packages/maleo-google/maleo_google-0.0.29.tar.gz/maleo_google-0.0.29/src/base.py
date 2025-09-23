from maleo.logging.config import Config
from maleo.logging.logger import Client
from maleo.schemas.service import ServiceContext, OptionalServiceContext
from maleo.schemas.operation.context import generate
from maleo.schemas.operation.enums import Origin, Layer, Target
from maleo.schemas.resource import Resource, ResourceIdentifier
from maleo.types.misc import OptionalPathOrString
from .credential import load
from .types import OptionalCredentials


RESOURCE = Resource(
    identifiers=[ResourceIdentifier(key="google", name="Google", slug="google")],
    details=None,
)


class GoogleClientManager:
    def __init__(
        self,
        key: str,
        name: str,
        log_config: Config,
        service_context: OptionalServiceContext = None,
        credentials: OptionalCredentials = None,
        credentials_path: OptionalPathOrString = None,
    ) -> None:
        self._key = key
        self._name = name

        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )

        self._logger = Client(
            environment=self._service_context.environment,
            service_key=self._service_context.key,
            client_key=self._key,
            config=log_config,
        )

        if (credentials is None and credentials_path is None) or (
            credentials is not None and credentials_path is not None
        ):
            raise ValueError(
                "Only either 'credentials' and 'credentials_path' must be given"
            )

        if credentials is not None:
            self._credentials = credentials
        else:
            self._credentials = load(credentials_path)

        self._operation_context = generate(
            origin=Origin.CLIENT, layer=Layer.SERVICE, target=Target.INTERNAL
        )
