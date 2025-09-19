import logging
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from maleo.logging.enums import Level, LoggerType
from maleo.schemas.error.constants import ERROR_STATUS_CODE_MAP
from maleo.schemas.error.spec import ErrorSpecT
from maleo.schemas.error import ErrorT
from maleo.schemas.error.enums import Code as ErrorCode
from maleo.schemas.response import (
    ErrorResponseT,
    UnauthorizedResponse,
    UnprocessableEntityResponse,
    InternalServerErrorResponse,
    ERROR_RESPONSE_MAP,
    STATUS_RESPONSE_MAP,
)
from maleo.security.authentication import AuthenticationT
from maleo.security.authorization import AuthorizationT
from ..exc import MaleoException


def authentication_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        content=UnauthorizedResponse(
            other={
                "exc_type": type(exc).__name__,
                "exc_data": {
                    "message": str(exc),
                    "args": exc.args,
                },
            }
        ).model_dump(mode="json"),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


async def general_exception_handler(request: Request, exc: Exception):
    other = {
        "exc_type": type(exc).__name__,
        "exc_data": {
            "message": str(exc),
            "args": exc.args,
        },
    }

    # Get the first arg as a potential ErrorCode
    code = exc.args[0] if exc.args else None

    if isinstance(code, ErrorCode):
        error_code = code
    elif isinstance(code, str) and code in ErrorCode:
        error_code = ErrorCode[code]
    else:
        error_code = None

    if error_code:
        response_cls = ERROR_RESPONSE_MAP.get(error_code, None)
        status_code = ERROR_STATUS_CODE_MAP.get(error_code, None)

        if response_cls and status_code:
            response_obj = response_cls(other=other)  # type: ignore
            return JSONResponse(
                content=response_obj.model_dump(mode="json"),
                status_code=status_code,
            )

    return JSONResponse(
        content=InternalServerErrorResponse(other=other).model_dump(mode="json"),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        content=UnprocessableEntityResponse(
            other=jsonable_encoder(exc.errors())
        ).model_dump(mode="json"),
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        content=UnprocessableEntityResponse(other=exc.errors()).model_dump(mode="json"),
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    other = {
        "exc_type": type(exc).__name__,
        "exc_data": {
            "status_code": exc.status_code,
            "detail": exc.detail,
            "headers": exc.headers,
        },
    }

    if exc.status_code in STATUS_RESPONSE_MAP:
        model_cls = STATUS_RESPONSE_MAP[exc.status_code]
        return JSONResponse(
            content=model_cls(other=other).model_dump(mode="json"),  # type: ignore
            status_code=exc.status_code,
        )

    return JSONResponse(
        content=InternalServerErrorResponse(other=other).model_dump(mode="json"),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def maleo_exception_handler(
    request: Request,
    exc: MaleoException[
        AuthenticationT, AuthorizationT, ErrorResponseT, ErrorSpecT, ErrorT
    ],
):
    logger = logging.getLogger(
        f"{exc.service_context.environment} - {exc.service_context.key} - {LoggerType.EXCEPTION}"
    )

    operation = exc.generate_operation(exc.operation_type)

    operation.log(logger, Level.ERROR)

    return JSONResponse(
        content=exc.response.model_dump(mode="json"),
        status_code=exc.error_spec.status_code,
    )
