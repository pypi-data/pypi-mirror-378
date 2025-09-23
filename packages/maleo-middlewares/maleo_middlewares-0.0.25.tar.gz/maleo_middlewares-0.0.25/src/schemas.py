from pydantic import BaseModel, Field
from typing_extensions import Annotated
from maleo.enums.status import DataStatus as DataStatusEnum
from maleo.mixins.identity import DataIdentifier
from maleo.mixins.status import DataStatus
from maleo.types.string import ListOfStrings


class InactiveKeys(BaseModel):
    keys: ListOfStrings = Field(..., min_length=1, description="Inactive keys")


class User(DataStatus[DataStatusEnum], DataIdentifier):
    username: Annotated[str, Field(..., description="User's username", max_length=50)]
    email: Annotated[str, Field(..., description="User's email", max_length=255)]
    system_roles: Annotated[
        ListOfStrings, Field(..., description="User's system roles", min_length=1)
    ]


class UserOrganization(DataStatus[DataStatusEnum], DataIdentifier):
    user_id: Annotated[int, Field(..., description="User's ID", ge=1)]
    organization_id: Annotated[int, Field(..., description="Organization's ID", ge=1)]
    user_organization_roles: Annotated[
        ListOfStrings, Field(..., description="User's organization roles", min_length=1)
    ]
