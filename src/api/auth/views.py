# import logging
#
# from fastapi import APIRouter, HTTPException, Depends
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from starlette.responses import Response
#
# auth_router = APIRouter()
#
# # JWT 설정
# SECRET_KEY = "your_secret_key"
# ALGORITHM = "HS256"
#
# # OAuth2PasswordBearer는 로그인 후 토큰을 요청할 때 사용하는 경로를 정의
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
#
# # 세션을 유지하기 위한 secret key 설정
# auth_router.add_middleware(SessionMiddleware, secret_key="your_secret_key")
#
#
# # 로그인 처리 함수
# @auth_router.post("/login")
# async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
#     user = get_by_id(form_data.user_id)
#     if not user or user['password'] != form_data.password:
#         return {"error": "Invalid credentials"}
#
#     # 세션에 사용자 정보 저장
#     response.set_cookie(key="session", value=form_data.username, httponly=True, max_age=None)  # max_age=None로 영구 쿠키 설정
#     return {"message": "Login successful"}
#
# # 로그인한 사용자 정보 가져오기
# @app.get("/me")
# async def get_me(request: Request):
#     session = request.cookies.get("session")
#     if not session:
#         return {"error": "Not logged in"}
#     return {"username": session}