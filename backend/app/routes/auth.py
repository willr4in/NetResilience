from fastapi import APIRouter, Depends, Response, Cookie, status, HTTPException
from typing import Optional
from ..dependencies import get_auth_service
from ..services.auth_service import AuthService
from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from ..schemas.user import UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, response: Response, auth_service: AuthService = Depends(get_auth_service)):
    user = auth_service.register(data)
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 30,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax"
    )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(data: LoginRequest, response: Response, auth_service: AuthService = Depends(get_auth_service)):
    user = auth_service.login(data.email, data.password)
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 30,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax"
    )
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def refresh(response: Response, refresh_token: Optional[str] = Cookie(None), auth_service: AuthService = Depends(get_auth_service)):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен обновления отсутствует")
    
    new_access_token = auth_service.refresh_access_token(refresh_token)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=60 * 30,
        samesite="lax"
    )
    return TokenResponse(access_token=new_access_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response, refresh_token: Optional[str] = Cookie(None), auth_service: AuthService = Depends(get_auth_service)):
    if refresh_token:
        auth_service.logout(refresh_token)
    
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}