# import logging
# from typing import Optional
#
# from fastapi import HTTPException
# from starlette.requests import Request
# from starlette.status import HTTP_401_UNAUTHORIZED
#
# from src.api.auth.models import User, UserRegister, UserUpdate
#
# log = logging.getLogger(__name__)
#
# InvalidCredentialException = HTTPException(
#     status_code=HTTP_401_UNAUTHORIZED, detail=[{"msg": "Could not validate credentials"}]
# )
#
#
# def get(*, db_session, user_id: int) -> Optional[User]:
#     """Returns a user based on the given user id."""
#     return db_session.query(User).filter(User.id == user_id).one_or_none()
#
#
# def get_by_id(*, db_session, user_id: int) -> Optional[User]:
#     """Returns a user based on the given user id."""
#     return db_session.query(User).filter(User.id == user_id).one_or_none()
#
#
# def create(*, db_session, user_in: UserRegister) -> User:
#     """Creates a new user."""
#     password = bytes(user_in.password, "utf-8")
#     user = User(
#         **user_in.model_dump(exclude={"password"}), password=password
#     )
#
#     db_session.add(user)
#     db_session.commit()
#     return user
#
#
# def update(*, db_session, user: User, user_in: UserUpdate) -> User:
#     # 업데이트 가능한 필드 확인 후 변경
#     if user_in.password:
#         password = bytes(user_in.password, "utf-8")
#         user.password = password  # 비밀번호는 이미 UserUpdate에서 해싱 처리됨
#
#     if user_in.is_active is not None:
#         user.is_active = user_in.is_active
#
#     if user_in.is_admin is not None:
#         user.is_admin = user_in.is_admin
#
#     db_session.commit()
#     return user
#
#
#
#
# def get_current_user(request: Request) -> User:
#     """Attempts to get the current user depending on the configured authentication provider."""
#     if DISPATCH_AUTHENTICATION_PROVIDER_SLUG:
#         auth_plugin = plugins.get(DISPATCH_AUTHENTICATION_PROVIDER_SLUG)
#         user_email = auth_plugin.get_current_user(request)
#     else:
#         log.debug("No authentication provider. Default user will be used")
#         user_email = DISPATCH_AUTHENTICATION_DEFAULT_USER
#
#     if not user_email:
#         log.exception(
#             f"Unable to determine user email based on configured auth provider or no default auth user email defined. Provider: {DISPATCH_AUTHENTICATION_PROVIDER_SLUG}"
#         )
#         raise InvalidCredentialException
#
#     return get_or_create(
#         db_session=request.state.db,
#         organization=request.state.organization,
#         user_in=UserRegister(email=user_email),
#     )
#
#
# CurrentUser = Annotated[DispatchUser, Depends(get_current_user)]
