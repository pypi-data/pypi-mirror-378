from Crypto.PublicKey.RSA import RsaKey
from datetime import datetime, timezone
from fastapi.requests import HTTPConnection
from pydantic import ValidationError
from sqlalchemy import select
from starlette.authentication import AuthenticationBackend, AuthenticationError
from typing import Optional, Tuple, Union
from uuid import UUID
from maleo.crypto.token import decode
from maleo.database.enums import CacheOrigin, CacheLayer, Connection
from maleo.database.handlers import PostgreSQLHandler, RedisHandler
from maleo.database.utils import build_cache_key
from maleo.enums.expiration import Expiration
from maleo.enums.status import DataStatus
from maleo.schemas.connection import ConnectionContext
from maleo.security.authentication import RequestCredentials, RequestUser
from maleo.security.authorization import (
    Source,
    Scheme,
    Authorization,
    OptionalAuthorization,
)
from maleo.security.impersonation import (
    Source as ImpersonationSource,
    Impersonation,
    OptionalImpersonation,
)
from maleo.security.token import Domain, OldToken, BaseToken
from maleo.types.dict import StringToAnyDict
from maleo.types.string import ListOfStrings
from maleo.types.uuid import OptionalUUID
from .models import (
    Base,
    User as UserModel,
    Organization as OrganizationModel,
    UserOrganization as UserOrganizationModel,
)
from .schemas import User as UserSchema, UserOrganization as UserOrganizationSchema


class Backend(AuthenticationBackend):
    def __init__(
        self,
        *,
        database: PostgreSQLHandler[Base],
        cache: RedisHandler,
        public_key: RsaKey,
    ):
        super().__init__()
        self._database = database
        self._cache = cache
        self._namespace = self._cache.config.additional.build_namespace(
            use_self_base=True, origin=CacheOrigin.SERVICE, layer=CacheLayer.MIDDLEWARE
        )
        self._public_key = public_key

    def _define_authorization(self, conn: HTTPConnection) -> OptionalAuthorization:
        self.authorization = Authorization.extract(
            Source.STATE, conn=conn, auto_error=False
        )

    def _validate_token(
        self, decoded_token: StringToAnyDict
    ) -> Union[OldToken, BaseToken]:
        for model in (OldToken, BaseToken):
            try:
                return model.model_validate(decoded_token)
            except ValidationError:
                continue
        raise AuthenticationError("Token is invalid for all known token types")

    async def _get_user(
        self,
        user_id: UUID,
        exp: datetime,
        *,
        operation_id: UUID,
        connection_context: ConnectionContext,
        authorization: OptionalAuthorization = None,
        impersonation: OptionalImpersonation = None,
    ) -> UserSchema:
        cache_key = build_cache_key("user", str(user_id), namespace=self._namespace)
        redis = self._cache.manager.client.get(Connection.ASYNC)
        redis_data = await redis.get(cache_key)
        if redis_data is not None:
            return UserSchema.model_validate(redis_data)

        async with self._database.manager.session.get(
            Connection.ASYNC,
            operation_id=operation_id,
            connection_context=connection_context,
            authentication=None,
            authorization=authorization,
            impersonation=impersonation,
        ) as session:
            stmt = select(UserModel).filter(
                UserModel.uuid == user_id, UserModel.status == DataStatus.ACTIVE
            )

            # Execute and fetch results
            result = await session.execute(stmt)
            row = result.scalars().one_or_none()

            if row is None:
                raise AuthenticationError(
                    f"Can not find active User with ID: {user_id}"
                )

            data = UserSchema(
                id=row.id,
                uuid=row.uuid,
                status=row.status,
                username=row.username,
                email=row.email,
                system_roles=row.get_system_roles([DataStatus.ACTIVE]),
            )

        now = datetime.now(tz=timezone.utc)
        ex = min(int((exp - now).total_seconds()), Expiration.EXP_15MN.value)
        await redis.set(cache_key, data.model_dump_json(), ex)

        return data

    async def _get_user_organization(
        self,
        user_id: UUID,
        organization_id: UUID,
        exp: datetime,
        *,
        operation_id: UUID,
        connection_context: ConnectionContext,
        authorization: OptionalAuthorization = None,
        impersonation: OptionalImpersonation = None,
    ) -> UserOrganizationSchema:
        cache_key = build_cache_key(
            "user_organization",
            str(user_id),
            str(organization_id),
            namespace=self._namespace,
        )
        redis = self._cache.manager.client.get(Connection.ASYNC)
        redis_data = await redis.get(cache_key)
        if redis_data is not None:
            return UserOrganizationSchema.model_validate(redis_data)

        async with self._database.manager.session.get(
            Connection.ASYNC,
            operation_id=operation_id,
            connection_context=connection_context,
            authentication=None,
            authorization=authorization,
            impersonation=impersonation,
        ) as session:
            stmt = (
                select(UserOrganizationModel)
                .join(UserModel, UserOrganizationModel.user_id == UserModel.id)
                .join(
                    OrganizationModel,
                    UserOrganizationModel.organization_id == OrganizationModel.id,
                )
                .filter(
                    UserOrganizationModel.status == DataStatus.ACTIVE,
                    UserModel.uuid == user_id,
                    UserModel.status == DataStatus.ACTIVE,
                    OrganizationModel.uuid == organization_id,
                    OrganizationModel.status == DataStatus.ACTIVE,
                )
            )

            # Execute and fetch results
            result = await session.execute(stmt)
            row = result.scalars().one_or_none()

            if row is None:
                raise AuthenticationError(
                    f"Can not find active relation for User '{user_id}' and Organization '{organization_id}'"
                )

            data = UserOrganizationSchema(
                id=row.id,
                uuid=row.uuid,
                status=row.status,
                user_id=row.user_id,
                organization_id=row.organization_id,
                user_organization_roles=row.get_user_organization_roles(
                    [DataStatus.ACTIVE]
                ),
            )

        now = datetime.now(tz=timezone.utc)
        ex = min(int((exp - now).total_seconds()), Expiration.EXP_15MN.value)
        await redis.set(cache_key, data.model_dump_json(), ex)

        return data

    async def _get_credentials(
        self,
        user_id: UUID,
        organization_id: OptionalUUID,
        roles: ListOfStrings,
        exp: datetime,
        *,
        operation_id: UUID,
        connection_context: ConnectionContext,
        authorization: OptionalAuthorization = None,
        impersonation: OptionalImpersonation = None,
    ) -> Tuple[UserSchema, Optional[UserOrganizationSchema]]:
        user = await self._get_user(
            user_id,
            exp,
            operation_id=operation_id,
            connection_context=connection_context,
            authorization=authorization,
            impersonation=impersonation,
        )

        if organization_id is None:
            user_organization = None

            system_roles = user.system_roles
            if system_roles != roles:
                raise AuthenticationError(
                    f"Mismatched roles. Database: {system_roles}, Token: {roles}"
                )
        else:
            user_organization = await self._get_user_organization(
                user_id,
                organization_id,
                exp,
                operation_id=operation_id,
                connection_context=connection_context,
                authorization=authorization,
                impersonation=impersonation,
            )

            user_organization_roles = user_organization.user_organization_roles

            if user_organization_roles != roles:
                raise AuthenticationError(
                    f"Mismatched roles. Database: {user_organization_roles}, Token: {roles}"
                )

        return user, user_organization

    async def authenticate(
        self, conn: HTTPConnection
    ) -> Tuple[RequestCredentials, RequestUser]:
        """Authentication flow"""
        authorization = self._define_authorization(conn)
        if authorization is None:
            return RequestCredentials(), RequestUser()

        if authorization.scheme is Scheme.API_KEY:
            raise AuthenticationError("API Key authentication is not yet implemented")

        operation_id = getattr(conn.state, "operation_id", None)
        if not operation_id or not isinstance(operation_id, UUID):
            raise AuthenticationError("Unable to determine operation_id")

        connection_context = ConnectionContext.from_connection(conn)
        impersonation = Impersonation.extract(ImpersonationSource.STATE, conn=conn)

        token = authorization.credentials
        try:
            decoded_token = decode(token, key=self._public_key)
        except Exception as e:
            raise AuthenticationError(
                f"Unexpected error occured while decoding token: {str(e)}"
            )

        roles: ListOfStrings = []

        validated_token = self._validate_token(decoded_token)

        if isinstance(validated_token, OldToken):
            exp = validated_token.exp_dt
            if validated_token.sr not in ("administrator", "user"):
                raise AuthenticationError(
                    f"Invalid value for claim 'sr': {validated_token.sr}"
                )

            if validated_token.sr == "administrator":
                if (
                    validated_token.o_i is not None
                    or validated_token.o_uu is not None
                    or validated_token.o_k is not None
                    or validated_token.o_ot is not None
                    or validated_token.uor is not None
                ):
                    raise AuthenticationError(
                        "All organization-related claims must be None for Administrator token"
                    )
                roles = ["administrator"]
            elif validated_token.sr == "user":
                if (
                    validated_token.o_i is None
                    or validated_token.o_uu is None
                    or validated_token.o_k is None
                    or validated_token.o_ot is None
                    or validated_token.uor is None
                ):
                    raise AuthenticationError(
                        "All organization-related claims can not be None for User token"
                    )
                roles = validated_token.uor

            user_id = validated_token.u_uu
            organization_id = validated_token.o_uu

        elif isinstance(validated_token, BaseToken):
            exp = datetime.fromtimestamp(validated_token.exp)
            if validated_token.d is Domain.SYSTEM:
                if validated_token.o is not None:
                    raise AuthenticationError(
                        "Claim 'o' must be 'None' for SystemToken"
                    )

            elif validated_token.d is Domain.TENANT:
                if validated_token.o is None:
                    raise AuthenticationError(
                        "Claim 'o' can not be 'None' for TenantToken"
                    )

            user_id = validated_token.sub
            organization_id = validated_token.o
            roles = validated_token.r

        else:
            raise AuthenticationError("Unable to determine token type")

        user, user_organization = await self._get_credentials(
            user_id,
            organization_id,
            roles,
            exp,
            operation_id=operation_id,
            connection_context=connection_context,
            authorization=authorization,
            impersonation=impersonation,
        )

        organization_id = None if user_organization is None else user_organization.uuid
        roles = (
            user.system_roles
            if user_organization is None
            else user_organization.user_organization_roles
        )
        domain = Domain.SYSTEM if user_organization is None else Domain.TENANT
        scopes = [f"{domain}:{role}" for role in roles]

        request_credentials = RequestCredentials(
            user_id=user.uuid,
            organization_id=organization_id,
            roles=(
                user.system_roles
                if user_organization is None
                else user_organization.user_organization_roles
            ),
            scopes=["authenticated"] + scopes,
        )

        request_user = RequestUser(
            authenticated=True, username=user.username, email=user.email
        )

        return request_credentials, request_user
