import httpx
from typing import Generic, Literal, Mapping, Optional, Type, overload
from uuid import uuid4
from maleo.logging.enums import Level
from maleo.logging.logger import Base
from maleo.schemas.contexts.service import ServiceContext
from maleo.schemas.contexts.request import RequestContext
from maleo.schemas.error.enums import Code as ErrorCode
from maleo.schemas.operation.context import Context
from maleo.schemas.operation.enums import OperationType
from maleo.schemas.operation.mixins import Timestamp
from maleo.schemas.operation.action.resource import AllResourceOperationAction
from maleo.schemas.resource import AggregateField, Resource
from maleo.schemas.response import ErrorResponse
from maleo.security.authentication import AuthenticationT
from maleo.security.authorization import AuthorizationT
from maleo.security.impersonation import Impersonation
from maleo.types.string import OptionalString
from maleo.types.uuid import OptionalUUID
from .exc import (
    MaleoException,
    BadRequest,
    Unauthorized,
    Forbidden,
    NotFound,
    MethodNotAllowed,
    Conflict,
    UnprocessableEntity,
    TooManyRequests,
    InternalServerError,
    NotImplemented,
    BadGateway,
    ServiceUnavailable,
    AllException,
    AllExceptionType,
)


class MaleoExceptionFactory(
    Generic[
        AuthenticationT,
        AuthorizationT,
    ],
):
    STATUS_EXCEPTION_MAP: Mapping[int, Type[MaleoException]] = {
        400: BadRequest[AuthenticationT, AuthorizationT],
        401: Unauthorized[AuthenticationT, AuthorizationT],
        403: Forbidden[AuthenticationT, AuthorizationT],
        404: NotFound[AuthenticationT, AuthorizationT],
        405: MethodNotAllowed[AuthenticationT, AuthorizationT],
        409: Conflict[AuthenticationT, AuthorizationT],
        422: UnprocessableEntity[AuthenticationT, AuthorizationT],
        429: TooManyRequests[AuthenticationT, AuthorizationT],
        500: InternalServerError[AuthenticationT, AuthorizationT],
        501: NotImplemented[AuthenticationT, AuthorizationT],
        502: BadGateway[AuthenticationT, AuthorizationT],
        503: ServiceUnavailable[AuthenticationT, AuthorizationT],
    }

    @overload
    @classmethod
    def get_exception_cls(
        cls,
        status_code: Literal[400],
        /,
    ) -> Type[BadRequest[AuthenticationT, AuthorizationT]]: ...
    @overload
    @classmethod
    def get_exception_cls(
        cls,
        status_code: Literal[401],
        /,
    ) -> Type[Unauthorized[AuthenticationT, AuthorizationT]]: ...
    @overload
    @classmethod
    def get_exception_cls(
        cls,
        status_code: Literal[403],
        /,
    ) -> Type[Forbidden[AuthenticationT, AuthorizationT]]: ...
    @overload
    @classmethod
    def get_exception_cls(
        cls,
        status_code: Literal[404],
        /,
    ) -> Type[NotFound[AuthenticationT, AuthorizationT]]: ...
    @overload
    @classmethod
    def get_exception_cls(
        cls,
        status_code: Literal[405],
        /,
    ) -> Type[MethodNotAllowed[AuthenticationT, AuthorizationT]]: ...
    @overload
    @classmethod
    def get_exception_cls(
        cls,
        status_code: Literal[409],
        /,
    ) -> Type[BadRequest[AuthenticationT, AuthorizationT]]: ...
    @overload
    @classmethod
    def get_exception_cls(
        cls,
        status_code: Literal[422],
        /,
    ) -> Type[BadRequest[AuthenticationT, AuthorizationT]]: ...
    @overload
    @classmethod
    def get_exception_cls(
        cls,
        status_code: Literal[429],
        /,
    ) -> Type[BadRequest[AuthenticationT, AuthorizationT]]: ...
    @overload
    @classmethod
    def get_exception_cls(
        cls,
        status_code: Literal[500],
        /,
    ) -> Type[BadRequest[AuthenticationT, AuthorizationT]]: ...
    @overload
    @classmethod
    def get_exception_cls(
        cls,
        status_code: Literal[501],
        /,
    ) -> Type[BadRequest[AuthenticationT, AuthorizationT]]: ...
    @overload
    @classmethod
    def get_exception_cls(
        cls,
        status_code: Literal[502],
        /,
    ) -> Type[BadRequest[AuthenticationT, AuthorizationT]]: ...
    @overload
    @classmethod
    def get_exception_cls(
        cls,
        status_code: Literal[503],
        /,
    ) -> Type[BadRequest[AuthenticationT, AuthorizationT]]: ...
    @classmethod
    def get_exception_cls(
        cls,
        status_code: int,
        /,
    ) -> AllExceptionType:
        if status_code == 400:
            return BadRequest[AuthenticationT, AuthorizationT]
        elif status_code == 401:
            return Unauthorized[AuthenticationT, AuthorizationT]
        elif status_code == 403:
            return Forbidden[AuthenticationT, AuthorizationT]
        elif status_code == 404:
            return NotFound[AuthenticationT, AuthorizationT]
        elif status_code == 405:
            return MethodNotAllowed[AuthenticationT, AuthorizationT]
        elif status_code == 409:
            return Conflict[AuthenticationT, AuthorizationT]
        elif status_code == 422:
            return UnprocessableEntity[AuthenticationT, AuthorizationT]
        elif status_code == 429:
            return TooManyRequests[AuthenticationT, AuthorizationT]
        elif status_code == 500:
            return InternalServerError[AuthenticationT, AuthorizationT]
        elif status_code == 501:
            return NotImplemented[AuthenticationT, AuthorizationT]
        elif status_code == 502:
            return BadGateway[AuthenticationT, AuthorizationT]
        elif status_code == 503:
            return ServiceUnavailable[AuthenticationT, AuthorizationT]
        return InternalServerError[AuthenticationT, AuthorizationT]

    def __init__(
        self,
        *,
        logger: Optional[Base] = None,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        request_context: Optional[RequestContext] = None,
        authentication: AuthenticationT = None,
        authorization: AuthorizationT = None,
        impersonation: Optional[Impersonation] = None,
    ) -> None:
        self._logger = logger

        self.service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )

        self.operation_id = operation_id if operation_id is not None else uuid4()
        self.operation_context = operation_context

        self.request_context = request_context
        self.authentication = authentication
        self.authorization = authorization
        self.impersonation = impersonation

        self._common_exception_kwargs = {
            "service_context": self.service_context,
            "operation_id": self.operation_id,
            "operation_context": self.operation_context,
            "request_context": self.request_context,
            "authentication": self.authentication,
            "authorization": self.authorization,
            "impersonation": self.impersonation,
        }

    @overload
    def from_httpx(
        self,
        operation_type: Literal[OperationType.REQUEST],
        *,
        response: httpx.Response,
        action: AllResourceOperationAction,
        timestamp: Optional[Timestamp] = None,
        summary: OptionalString = None,
    ) -> AllException: ...
    @overload
    def from_httpx(
        self,
        operation_type: Literal[OperationType.RESOURCE],
        *,
        response: httpx.Response,
        action: AllResourceOperationAction,
        resource: Resource,
        timestamp: Optional[Timestamp] = None,
        summary: OptionalString = None,
    ) -> AllException: ...
    def from_httpx(
        self,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        *,
        response: httpx.Response,
        action: AllResourceOperationAction,
        resource: Optional[Resource] = None,
        timestamp: Optional[Timestamp] = None,
        summary: OptionalString = None,
    ) -> AllException:
        if not response.is_error:
            raise ValueError(
                ErrorCode.BAD_REQUEST,
                "Failed generating MaleoException from httpx response, Response is not error.",
            )

        if operation_type is OperationType.RESOURCE:
            if resource is None:
                raise ValueError(
                    ErrorCode.BAD_REQUEST,
                    "Failed generating MaleoException from httpx response, Resource is not given.",
                )

        operation_timestamp = timestamp if timestamp is not None else Timestamp.now()

        exception_cls = self.STATUS_EXCEPTION_MAP.get(
            response.status_code, InternalServerError[AuthenticationT, AuthorizationT]
        )
        if operation_type is OperationType.REQUEST:
            operation_summary = (
                summary
                if summary is not None
                else "Request operation failed due to httpx error response"
            )
            exception = exception_cls(
                operation_type=operation_type,
                operation_action=action,
                operation_timestamp=operation_timestamp,
                operation_summary=operation_summary,
                response=response.content,
                **self._common_exception_kwargs,
            )
            operation = exception.generate_operation(operation_type)
        elif operation_type is OperationType.RESOURCE:
            if resource is None:
                raise ValueError(
                    ErrorCode.BAD_REQUEST,
                    "Failed generating MaleoException from httpx response, Resource is not given.",
                )
            operation_summary = (
                summary
                if summary is not None
                else f"Failed requesting '{resource.aggregate(AggregateField.KEY)}' due to httpx error response"
            )
            response_json = ErrorResponse.model_validate(response.json())
            exception = exception_cls(
                operation_type=operation_type,
                operation_action=action,
                operation_timestamp=operation_timestamp,
                operation_summary=operation_summary,
                resource=resource,
                response=response_json,
                **self._common_exception_kwargs,
            )
            operation = exception.generate_operation(operation_type)

        if self._logger is not None:
            operation = exception.generate_operation(operation_type)
            operation.log(self._logger, Level.ERROR)

        return exception  # type: ignore
