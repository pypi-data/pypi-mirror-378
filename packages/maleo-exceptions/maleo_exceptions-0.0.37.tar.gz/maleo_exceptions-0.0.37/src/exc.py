import traceback as tb
from fastapi.responses import JSONResponse
from typing import Any, Generic, Literal, Optional, Type, Union, overload
from uuid import uuid4
from maleo.schemas.contexts.request import RequestContext
from maleo.schemas.contexts.response import ResponseContext
from maleo.schemas.contexts.service import ServiceContext
from maleo.schemas.error.enums import Code as ErrorCode
from maleo.schemas.error.metadata import ErrorMetadata
from maleo.schemas.error.spec import (
    ErrorSpecT,
    BadRequestErrorSpec,
    UnauthorizedErrorSpec,
    ForbiddenErrorSpec,
    NotFoundErrorSpec,
    MethodNotAllowedErrorSpec,
    ConflictErrorSpec,
    UnprocessableEntityErrorSpec,
    TooManyRequestsErrorSpec,
    InternalServerErrorSpec,
    DatabaseErrorSpec,
    NotImplementedErrorSpec,
    BadGatewayErrorSpec,
    ServiceUnavailableErrorSpec,
)
from maleo.schemas.error import (
    ErrorT,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    MethodNotAllowedError,
    ConflictError,
    UnprocessableEntityError,
    TooManyRequestsError,
    InternalServerError as InternalServerErrorSchema,
    DatabaseError as DatabaseErrorSchema,
    NotImplementedError,
    BadGatewayError,
    ServiceUnavailableError,
)
from maleo.schemas.operation.action.resource import (
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
    DeleteResourceOperationAction,
    AllResourceOperationAction,
)
from maleo.schemas.operation.action.system import SystemOperationAction
from maleo.schemas.operation.context import Context
from maleo.schemas.operation.enums import OperationType
from maleo.schemas.operation.mixins import Timestamp
from maleo.schemas.operation.request import (
    CreateFailedRequestOperation,
    ReadFailedRequestOperation,
    UpdateFailedRequestOperation,
    DeleteFailedRequestOperation,
    Factory as RequestOperationFactory,
)
from maleo.schemas.operation.resource import (
    CreateFailedResourceOperation,
    ReadFailedResourceOperation,
    UpdateFailedResourceOperation,
    DeleteFailedResourceOperation,
    Factory as ResourceOperationFactory,
)
from maleo.schemas.operation.system import FailedSystemOperation
from maleo.schemas.resource import Resource
from maleo.schemas.response import (
    ErrorResponseT,
    BadRequestResponse,
    UnauthorizedResponse,
    ForbiddenResponse,
    NotFoundResponse,
    MethodNotAllowedResponse,
    ConflictResponse,
    UnprocessableEntityResponse,
    TooManyRequestsResponse,
    InternalServerErrorResponse,
    DatabaseErrorResponse,
    NotImplementedResponse,
    BadGatewayResponse,
    ServiceUnavailableResponse,
)
from maleo.security.authentication import AuthenticationT
from maleo.security.authorization import AuthorizationT
from maleo.security.impersonation import Impersonation
from maleo.types.string import ListOfStrings, OptionalString
from maleo.types.uuid import OptionalUUID


class MaleoException(
    Exception,
    Generic[
        AuthenticationT,
        AuthorizationT,
        ErrorResponseT,
        ErrorSpecT,
        ErrorT,
    ],
):
    error_response_cls: Type[ErrorResponseT]
    error_spec_cls: Type[ErrorSpecT]
    error_cls: Type[ErrorT]

    @overload
    def __init__(
        self,
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST],
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AllResourceOperationAction,
        operation_timestamp: Optional[Timestamp] = None,
        operation_summary: OptionalString = None,
        request_context: RequestContext,
        authentication: AuthenticationT = None,
        authorization: AuthorizationT = None,
        impersonation: Optional[Impersonation] = None,
        response: Optional[ErrorResponseT] = None,
    ) -> None: ...
    @overload
    def __init__(
        self,
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.RESOURCE],
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AllResourceOperationAction,
        resource: Resource,
        operation_timestamp: Optional[Timestamp] = None,
        operation_summary: OptionalString = None,
        request_context: RequestContext,
        authentication: AuthenticationT = None,
        authorization: AuthorizationT = None,
        impersonation: Optional[Impersonation] = None,
        response: Optional[ErrorResponseT] = None,
    ) -> None: ...
    @overload
    def __init__(
        self,
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.SYSTEM],
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: SystemOperationAction,
        operation_timestamp: Optional[Timestamp] = None,
        operation_summary: OptionalString = None,
        request_context: RequestContext,
        authentication: AuthenticationT = None,
        authorization: AuthorizationT = None,
        impersonation: Optional[Impersonation] = None,
        response: Optional[ErrorResponseT] = None,
    ) -> None: ...
    def __init__(
        self,
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[AllResourceOperationAction, SystemOperationAction],
        resource: Optional[Resource] = None,
        operation_timestamp: Optional[Timestamp] = None,
        operation_summary: OptionalString = None,
        request_context: Optional[RequestContext] = None,
        authentication: AuthenticationT = None,
        authorization: AuthorizationT = None,
        impersonation: Optional[Impersonation] = None,
        response: Optional[ErrorResponseT] = None,
    ) -> None:
        super().__init__(*args)
        self.details = details
        self.operation_type = operation_type

        self.service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )

        self.operation_id = operation_id if operation_id is not None else uuid4()
        self.operation_context = operation_context
        self.operation_action = operation_action
        self.resource = resource

        self.operation_timestamp = (
            operation_timestamp if operation_timestamp is not None else Timestamp.now()
        )

        self.operation_summary = (
            operation_summary
            if operation_summary is not None
            else f"{self.operation_type.capitalize()} operation failed due to exception being raised"
        )

        self.request_context = request_context
        self.authentication = authentication
        self.authorization = authorization
        self.impersonation = impersonation

        self._common_operation_kwargs = {
            "service_context": self.service_context,
            "id": self.operation_id,
            "context": self.operation_context,
            "timestamp": self.operation_timestamp,
            "summary": self.operation_summary,
            "error": self.error,
            "request_context": self.request_context,
            "authentication": self.authentication,
            "authorization": self.authorization,
            "impersonation": self.impersonation,
        }

        if response is not None:
            self.response: ErrorResponseT = response
            if self.response.other is None and self.details is not None:
                self.response.other = self.details
        else:
            # This line will not break due to
            # the fields already given default values
            self.response: ErrorResponseT = self.error_response_cls(other=self.details)  # type: ignore

        # Error-related initialization
        # The following lines will not break due to
        # the fields already given default values
        self.error_spec: ErrorSpecT = self.error_spec_cls()  # type: ignore
        self.error_metadata = ErrorMetadata(
            details=self.details, traceback=self.traceback
        )
        self.error: ErrorT = self.error_cls.model_validate(
            {**self.error_spec.model_dump(), **self.error_metadata.model_dump()}
        )

    @property
    def traceback(self) -> ListOfStrings:
        return tb.format_exception(self)

    @overload
    def generate_operation(
        self,
        operation_type: Literal[OperationType.REQUEST],
        /,
    ) -> Union[
        CreateFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT],
        ReadFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT],
        UpdateFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT],
        DeleteFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT],
    ]: ...
    @overload
    def generate_operation(
        self,
        operation_type: Literal[OperationType.RESOURCE],
        /,
    ) -> Union[
        CreateFailedResourceOperation[
            ErrorT, AuthenticationT, AuthorizationT, ErrorResponseT
        ],
        ReadFailedResourceOperation[
            ErrorT, AuthenticationT, AuthorizationT, ErrorResponseT
        ],
        UpdateFailedResourceOperation[
            ErrorT, AuthenticationT, AuthorizationT, ErrorResponseT
        ],
        DeleteFailedResourceOperation[
            ErrorT, AuthenticationT, AuthorizationT, ErrorResponseT
        ],
    ]: ...
    @overload
    def generate_operation(
        self,
        operation_type: Literal[OperationType.SYSTEM],
        /,
    ) -> FailedSystemOperation[
        ErrorT, AuthenticationT, AuthorizationT, ErrorResponseT
    ]: ...
    def generate_operation(
        self,
        operation_type: OperationType,
        /,
    ) -> Union[
        CreateFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT],
        ReadFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT],
        UpdateFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT],
        DeleteFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT],
        CreateFailedResourceOperation[
            ErrorT, AuthenticationT, AuthorizationT, ErrorResponseT
        ],
        ReadFailedResourceOperation[
            ErrorT, AuthenticationT, AuthorizationT, ErrorResponseT
        ],
        UpdateFailedResourceOperation[
            ErrorT, AuthenticationT, AuthorizationT, ErrorResponseT
        ],
        DeleteFailedResourceOperation[
            ErrorT, AuthenticationT, AuthorizationT, ErrorResponseT
        ],
        FailedSystemOperation[ErrorT, AuthenticationT, AuthorizationT, ErrorResponseT],
    ]:
        if operation_type != self.operation_type:
            raise ValueError(
                ErrorCode.INTERNAL_SERVER_ERROR,
                (
                    "Failed generating operation for MaleoException ",
                    "due to mismatched operation_type. ",
                    f"Expected '{self.operation_type}' ",
                    f"but received {operation_type}.",
                ),
            )

        if operation_type is OperationType.SYSTEM:
            if not isinstance(self.operation_action, SystemOperationAction):
                raise ValueError(
                    ErrorCode.BAD_REQUEST,
                    f"Invalid operation_action to generate system operation: {type(self.operation_action)}",
                )
            return FailedSystemOperation[
                ErrorT, AuthenticationT, AuthorizationT, ErrorResponseT
            ](
                **self._common_operation_kwargs,
                action=self.operation_action,
                response=self.response,
            )
        else:
            if not isinstance(
                self.operation_action,
                (
                    CreateResourceOperationAction,
                    ReadResourceOperationAction,
                    UpdateResourceOperationAction,
                    DeleteResourceOperationAction,
                ),
            ):
                raise ValueError(
                    ErrorCode.BAD_REQUEST,
                    f"Invalid operation_action to generate {operation_type} operation: {type(self.operation_action)}",
                )

            if operation_type is OperationType.REQUEST:
                response = JSONResponse(
                    content=self.response.model_dump(mode="json"),
                    status_code=self.error_spec.status_code,
                )
                response_context = ResponseContext(
                    status_code=response.status_code,
                    media_type=response.media_type,
                    headers=response.headers.items(),
                )

                return RequestOperationFactory.generate_failed(
                    self.operation_action,
                    **self._common_operation_kwargs,
                    response=response.body,
                    response_context=response_context,
                )
            elif operation_type is OperationType.RESOURCE:
                if self.resource is None:
                    raise ValueError(
                        ErrorCode.BAD_REQUEST,
                        "Failed generating resource operation from MaleoException. Resource is not given",
                    )
                return ResourceOperationFactory.generate_failed(
                    self.operation_action,
                    **self._common_operation_kwargs,
                    resource=self.resource,
                    response=self.response,
                )


class ClientException(
    MaleoException[
        AuthenticationT,
        AuthorizationT,
        ErrorResponseT,
        ErrorSpecT,
        ErrorT,
    ],
    Generic[
        AuthenticationT,
        AuthorizationT,
        ErrorResponseT,
        ErrorSpecT,
        ErrorT,
    ],
):
    """Base class for all client error (HTTP 4xx) responses"""


class BadRequest(
    ClientException[
        AuthenticationT,
        AuthorizationT,
        BadRequestResponse,
        BadRequestErrorSpec,
        BadRequestError,
    ],
    Generic[AuthenticationT, AuthorizationT],
):
    error_response_cls = BadRequestResponse
    error_spec_cls = BadRequestErrorSpec
    error_cls = BadRequestError


class Unauthorized(
    ClientException[
        AuthenticationT,
        AuthorizationT,
        UnauthorizedResponse,
        UnauthorizedErrorSpec,
        UnauthorizedError,
    ],
    Generic[AuthenticationT, AuthorizationT],
):
    error_response_cls = UnauthorizedResponse
    error_spec_cls = UnauthorizedErrorSpec
    error_cls = UnauthorizedError


class Forbidden(
    ClientException[
        AuthenticationT,
        AuthorizationT,
        ForbiddenResponse,
        ForbiddenErrorSpec,
        ForbiddenError,
    ],
    Generic[AuthenticationT, AuthorizationT],
):
    error_response_cls = ForbiddenResponse
    error_spec_cls = ForbiddenErrorSpec
    error_cls = ForbiddenError


class NotFound(
    ClientException[
        AuthenticationT,
        AuthorizationT,
        NotFoundResponse,
        NotFoundErrorSpec,
        NotFoundError,
    ],
    Generic[AuthenticationT, AuthorizationT],
):
    error_response_cls = NotFoundResponse
    error_spec_cls = NotFoundErrorSpec
    error_cls = NotFoundError


class MethodNotAllowed(
    ClientException[
        AuthenticationT,
        AuthorizationT,
        MethodNotAllowedResponse,
        MethodNotAllowedErrorSpec,
        MethodNotAllowedError,
    ],
    Generic[AuthenticationT, AuthorizationT],
):
    error_response_cls = MethodNotAllowedResponse
    error_spec_cls = MethodNotAllowedErrorSpec
    error_cls = MethodNotAllowedError


class Conflict(
    ClientException[
        AuthenticationT,
        AuthorizationT,
        ConflictResponse,
        ConflictErrorSpec,
        ConflictError,
    ],
    Generic[AuthenticationT, AuthorizationT],
):
    error_response_cls = ConflictResponse
    error_spec_cls = ConflictErrorSpec
    error_cls = ConflictError


class UnprocessableEntity(
    ClientException[
        AuthenticationT,
        AuthorizationT,
        UnprocessableEntityResponse,
        UnprocessableEntityErrorSpec,
        UnprocessableEntityError,
    ],
    Generic[AuthenticationT, AuthorizationT],
):
    error_response_cls = UnprocessableEntityResponse
    error_spec_cls = UnprocessableEntityErrorSpec
    error_cls = UnprocessableEntityError


class TooManyRequests(
    ClientException[
        AuthenticationT,
        AuthorizationT,
        TooManyRequestsResponse,
        TooManyRequestsErrorSpec,
        TooManyRequestsError,
    ],
    Generic[AuthenticationT, AuthorizationT],
):
    error_response_cls = TooManyRequestsResponse
    error_spec_cls = TooManyRequestsErrorSpec
    error_cls = TooManyRequestsError


class ServerException(
    MaleoException[
        AuthenticationT,
        AuthorizationT,
        ErrorResponseT,
        ErrorSpecT,
        ErrorT,
    ],
    Generic[
        AuthenticationT,
        AuthorizationT,
        ErrorResponseT,
        ErrorSpecT,
        ErrorT,
    ],
):
    """Base class for all server error (HTTP 5xx) responses"""


class InternalServerError(
    ServerException[
        AuthenticationT,
        AuthorizationT,
        InternalServerErrorResponse,
        InternalServerErrorSpec,
        InternalServerErrorSchema,
    ],
    Generic[AuthenticationT, AuthorizationT],
):
    error_response_cls = InternalServerErrorResponse
    error_spec_cls = InternalServerErrorSpec
    error_cls = InternalServerErrorSchema


class DatabaseError(
    ServerException[
        AuthenticationT,
        AuthorizationT,
        DatabaseErrorResponse,
        DatabaseErrorSpec,
        DatabaseErrorSchema,
    ],
    Generic[AuthenticationT, AuthorizationT],
):
    error_response_cls = DatabaseErrorResponse
    error_spec_cls = DatabaseErrorSpec
    error_cls = DatabaseErrorSchema


class NotImplemented(
    ServerException[
        AuthenticationT,
        AuthorizationT,
        NotImplementedResponse,
        NotImplementedErrorSpec,
        NotImplementedError,
    ],
    Generic[AuthenticationT, AuthorizationT],
):
    error_response_cls = NotImplementedResponse
    error_spec_cls = NotImplementedErrorSpec
    error_cls = NotImplementedError


class BadGateway(
    ServerException[
        AuthenticationT,
        AuthorizationT,
        BadGatewayResponse,
        BadGatewayErrorSpec,
        BadGatewayError,
    ],
    Generic[AuthenticationT, AuthorizationT],
):
    error_response_cls = BadGatewayResponse
    error_spec_cls = BadGatewayErrorSpec
    error_cls = BadGatewayError


class ServiceUnavailable(
    ServerException[
        AuthenticationT,
        AuthorizationT,
        ServiceUnavailableResponse,
        ServiceUnavailableErrorSpec,
        ServiceUnavailableError,
    ],
    Generic[AuthenticationT, AuthorizationT],
):
    error_response_cls = ServiceUnavailableResponse
    error_spec_cls = ServiceUnavailableErrorSpec
    error_cls = ServiceUnavailableError
