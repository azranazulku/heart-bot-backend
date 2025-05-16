from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from schemas import UserCreate, UserOut, Token
from models import DB
from auth import create_access_token, verify_token

user_router = APIRouter(prefix="/users", tags=["users"])
db = DB()

# tokenUrl parametresi, login endpoint'inin tam path'i olmalı (prefix ile birlikte)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

@user_router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    existing_user = db.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    created_user = db.create_user(
        user.first_name, user.last_name, user.username,
        user.birth_date, user.email, user.password
    )
    return created_user

@user_router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.get_user_by_username(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # Şifre doğrulaması - db.verify_password fonksiyonunun doğru çalıştığından emin ol
    if not db.verify_password(form_data.password, user['password_hash']):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user['username']})
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.get("/me", response_model=UserOut)
def read_users_me(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    user = db.get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

