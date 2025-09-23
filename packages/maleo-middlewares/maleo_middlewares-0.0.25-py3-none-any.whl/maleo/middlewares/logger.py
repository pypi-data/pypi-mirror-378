import json
import traceback
from datetime import datetime
from fastapi import status, HTTPException, Request
from typing import Any
from starlette.middleware.base import RequestResponseEndpoint
from maleo.enums.connection import Header
from maleo.logging.enums import Level
from maleo.logging.logger import Middleware
from maleo.schemas.connection import ConnectionContext
from maleo.schemas.response import ResponseContext
from maleo.schemas.error import Factory as ErrorFactory
from maleo.schemas.operation.action.resource import (
    Factory as ResourceOperationActionFactory,
)
from maleo.schemas.operation.context import generate
from maleo.schemas.operation.enums import Origin, Layer, Target
from maleo.schemas.operation.extractor import extract_operation_id
from maleo.schemas.operation.mixins import Timestamp
from maleo.schemas.operation.request import (
    FailedFactory as FailedRequestOperationFactory,
    SuccessfulFactory as SuccessfulRequestOperationFactory,
)
from maleo.schemas.pagination import OptionalAnyPagination
from maleo.schemas.response import AnyDataResponse, ErrorFactory as ErrorResponseFactory
from maleo.schemas.service import ServiceContext, OptionalServiceContext
from maleo.security.authentication import BaseAuthentication
from maleo.security.authorization import (
    Source as AuthorizationSource,
    Authorization,
    OptionalAuthorization,
)
from maleo.security.impersonation import Source as ImpersonationSource, Impersonation
from maleo.utils.extractor import ResponseBodyExtractor


def log(logger: Middleware, *, service_context: OptionalServiceContext = None):
    service_context = (
        service_context if service_context is not None else ServiceContext.from_env()
    )

    operation_context = generate(
        origin=Origin.SERVICE,
        layer=Layer.MIDDLEWARE,
        target=Target.INTERNAL,
    )

    async def dependency(request: Request, call_next: RequestResponseEndpoint):
        response = await call_next(request)

        content_type = response.headers.get(Header.CONTENT_TYPE)

        if content_type is None or (
            content_type is not None and "application/json" not in content_type.lower()
        ):
            return response

        operation_id = extract_operation_id(request=request)
        operation_action = ResourceOperationActionFactory.extract(
            request=request, strict=False
        )

        executed_at = request.state.executed_at
        if not isinstance(executed_at, datetime):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Executed At timestamp is not a datetime {executed_at}",
            )

        completed_at = request.state.completed_at
        if not isinstance(completed_at, datetime):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Completed At timestamp is not a datetime {completed_at}",
            )

        duration = request.state.duration
        if not isinstance(duration, float):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Duration is not a float {duration}",
            )

        operation_timestamp = Timestamp(
            executed_at=executed_at, completed_at=completed_at, duration=duration
        )

        connection_context = ConnectionContext.from_connection(request)
        authentication: BaseAuthentication = BaseAuthentication.extract(request)
        authorization = Authorization.extract(AuthorizationSource.STATE, conn=request)
        impersonation = Impersonation.extract(ImpersonationSource.STATE, conn=request)

        response_context = ResponseContext(
            status_code=response.status_code,
            media_type=response.media_type,
            headers=response.headers.items(),
        )

        response_body, final_response = await ResponseBodyExtractor.async_extract(
            response
        )
        try:
            json_dict = json.loads(response_body)
            if 200 <= final_response.status_code < 400:
                validated_response = AnyDataResponse[
                    Any, OptionalAnyPagination, Any
                ].model_validate(json_dict)
                operation = SuccessfulRequestOperationFactory[
                    BaseAuthentication, OptionalAuthorization
                ].generate(
                    operation_action,
                    service_context=service_context,
                    id=operation_id,
                    context=operation_context,
                    timestamp=operation_timestamp,
                    summary="Successfully processed request",
                    connection_context=connection_context,
                    authentication=authentication,
                    authorization=authorization,
                    impersonation=impersonation,
                    response=validated_response,
                    response_context=response_context,
                )
                operation.log(logger, Level.INFO)
            elif 400 <= final_response.status_code <= 500:
                response_cls = ErrorResponseFactory.cls_from_code(
                    final_response.status_code
                )
                validated_response = response_cls.model_validate(json_dict)
                error_cls = ErrorFactory.cls_from_code(final_response.status_code)
                operation = FailedRequestOperationFactory[
                    error_cls, BaseAuthentication, OptionalAuthorization, response_cls
                ].generate(
                    operation_action,
                    service_context=service_context,
                    id=operation_id,
                    context=operation_context,
                    timestamp=operation_timestamp,
                    summary="Failed processing request",
                    error=error_cls(),
                    connection_context=connection_context,
                    authentication=authentication,
                    authorization=authorization,
                    impersonation=impersonation,
                    response=validated_response,
                    response_context=response_context,
                )
                operation.log(logger, Level.ERROR)
        except Exception:
            print(
                "Failed loading response body to json for operation logging :\n",
                traceback.format_exc(),
            )

        return response

    return dependency
