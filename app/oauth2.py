# in this file, you will be setting up the oauth2 using JWT token and use the pyjwt library

from fastapi import Depends, status, HTTPException
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from . import schemas
from fastapi.security import OAuth2PasswordBearer
# the token needs a secret_key, an hashing algorithm (we are using HS256) and an expiration time for the token
# the expiration time suggest how long the user should be logged in and if there's no expiration time, the user is logged in forever

SECRET_KEY = "BJVkBNpZ723DhWE5ahh2r-KS4T0zbvT4J9_zba1TVryYnU0PJ3PLC6NX9HypQ4po9Aw"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login') # this is going to be the login url


def create_access_token(data : dict): # the data is the payload which is of dictionary data type
    #copy the data to encode as you need not change it 
    to_encode = data.copy() # we are going to encode the data 

    # we will now use the timedelta function which is basically a function to calculate the difference or sum between two datetime object
    # we are going to add 30 minutes to the current time to get the expiration time of the token using the timedelta function
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp" : expire }) # updating the token to include the expiration time 

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # this function take the to_encode payload, secret_key and the algorithm

    return encoded_jwt

# now you can go back to the specific path operation to return the token to the user

#defining the function to verify the access token

def verify_access_token(token: str, credentials_exception): # passing a token of type string, and also passing the specific credentials exception (eg:- there is an issue with the jwt token or credentials doesn't match)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        id : str = str(payload.get("user_id"))

        if id is None:
            raise credentials_exception

        token_data = schemas.TokenData(id=id)
    except PyJWTError:
        raise credentials_exception
    
    return token_data

# now we are going to define another function get_current_user which will be passed as a dependency and will take the token first verify it and then extract the id of the user.
# and then we can fetch the user form the database and then add as a parameter into the path operation function

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code= status.HTTP_403_FORBIDDEN, 
                                          detail= f"Could not validate credentials", headers={"WWW-Authenticate": "bearer"})

    return verify_access_token(token, credentials_exception)