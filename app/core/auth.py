import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta

from app.core.config import settings


class AuthHandler:
    security = HTTPBearer()
    hasher = CryptContext(schemes=["bcrypt"])
    # secret = "SECRET"
    secret = settings.SECRET_KEY

    def encode_password(self, password):
        return self.hasher.hash(password)

    def verify_password(self, password, encoded_password):
        return self.hasher.verify(password, encoded_password)

    def encode_token(self, username):
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow(),
            'scope': 'access_token',
            'sub': username
        }

        return jwt.encode(payload, self.secret, algorithm=settings.ALGORITHM)

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=settings.ALGORITHM)
            if payload['scope'] == 'access_token':
                return payload['sub']
            raise HTTPException(status_code=401, detail='Invalid scope for token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token Expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid Token')

    def encode_refresh_token(self, username):
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow(),
            'scope': 'refresh_token',
            'sub': username
        }
        return jwt.encode(payload, self.secret, algorithm=settings.ALGORITHM)

    def decode_refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(refresh_token, self.secret, algorithms=settings.ALGORITHM)
            if payload['scope'] == 'refresh_token':
                username = payload['sub']
                new_token = self.encode_token(username)
                return new_token
            raise HTTPException(status_code=401, detail='Invalid scope for token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Refresh token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid refresh token')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)


auth = AuthHandler()
