import traceback
from datetime import datetime, timezone
from fastapi import status, Request
from fastapi.responses import Response, JSONResponse
from uuid import uuid4
from maleo.schemas.operation.action.resource import (
    Factory as ResourceOperationActionFactory,
)
from maleo.schemas.operation.enums import IdSource
from maleo.schemas.operation.extractor import extract_operation_id
from maleo.schemas.response import InternalServerErrorResponse
from maleo.security.authorization import Authorization
from maleo.security.impersonation import Impersonation
from .types import CallNext


async def assign_state(request: Request, call_next: CallNext[Response]):
    try:
        # Assign Operation Id
        operation_id = extract_operation_id(
            IdSource.HEADER, request=request, generate=True
        )
        request.state.operation_id = operation_id

        # Assign Operation action
        request.state.operation_action = ResourceOperationActionFactory.extract(
            request=request, from_state=False, strict=False
        )

        # Assign Connection Id
        request.state.connection_id = uuid4()

        executed_at = datetime.now(tz=timezone.utc)
        request.state.executed_at = executed_at

        # Assign Authorization
        Authorization.assign_to_state(request)

        # Assign impersonation
        Impersonation.assign_to_state(request)

        # Call and return response
        return await call_next(request)
    except Exception as e:
        print(
            "Unexpected error while assigning request state:\n",
            traceback.format_exc(),
        )
        return JSONResponse(
            content=InternalServerErrorResponse(
                message="Unexpected error while assigning request state",
                other={
                    "exc_type": type(e).__name__,
                    "exc_data": {
                        "message": str(e),
                        "args": e.args,
                    },
                },
            ).model_dump(mode="json"),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
