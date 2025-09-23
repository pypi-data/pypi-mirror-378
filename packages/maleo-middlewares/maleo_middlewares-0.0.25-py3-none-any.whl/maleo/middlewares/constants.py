from maleo.enums.request import Header, Method
from maleo.types.string import SequenceOfStrings


ALLOW_METHODS: SequenceOfStrings = (
    Method.GET.value,
    Method.POST.value,
    Method.PUT.value,
    Method.PATCH.value,
    Method.DELETE.value,
    Method.OPTIONS.value,
)

ALLOW_HEADERS: SequenceOfStrings = (
    Header.AUTHORIZATION.value,
    Header.CONTENT_TYPE.value,
    Header.X_CLIENT_ID.value,
    Header.X_CLIENT_SECRET.value,
    Header.X_OPERATION_ID.value,
    Header.X_ORGANIZATION_ID.value,
    Header.X_REQUEST_ID.value,
    Header.X_REQUESTED_AT.value,
    Header.X_SIGNATURE.value,
    Header.X_USER_ID.value,
)

EXPOSE_HEADERS: SequenceOfStrings = (
    Header.X_CLIENT_ID.value,
    Header.X_CLIENT_SECRET.value,
    Header.X_NEW_AUTHORIZATION.value,
    Header.X_OPERATION_ID.value,
    Header.X_ORGANIZATION_ID.value,
    Header.X_PROCESS_TIME.value,
    Header.X_REQUEST_ID.value,
    Header.X_REQUESTED_AT.value,
    Header.X_RESPONDED_AT.value,
    Header.X_SIGNATURE.value,
    Header.X_USER_ID.value,
)
