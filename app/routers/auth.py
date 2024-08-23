# this file will contain the logic and the api endpoints for user authentication

from fastapi import HTTPException, APIRouter, Depends, status, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, models, utils, oauth2
from ..database import get_db

router = APIRouter(
    tags= ["Authentication"]
)

@router.post("/login", response_model= schemas.Token)
def login(user_cred: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)): # basically, FastAPI is automatically going to store the credentials in the variable user_cred
    
    # remember OAuth2PasswordRequestForm will return the field as username ( AND NOT EMAIL ) and password that is, it will store the email in a field called username
    # so you just need to change the below line from "user_cred.email" to "user_cred.username"

    user = db.query(models.User).filter(models.User.email == user_cred.username).first()
    # NOTE:- The parameters such as the email and the password must be given as the "Body form-data" instead of the "Body raw"
    # the key will be "username" and "password" and then enter the email and password respectively.


    #verify if the email is valid and exists in the backend database
    if not user:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= f"Invalid Credentials")

    #verify if the password matches with the hashed password in the backend 
    if not utils.verify(user_cred.password, user.password):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= f"Invalid Credentials")
    
    # refer to the documentation of fastapi for jwt token authentication under security (OAuth2 with Password (and hashing), Bearer with JWT tokens)
    # here, we will create a token 
    # and then return the token

    access_token = oauth2.create_access_token(data= {"user_id" : user.id}) #remember the data is the payload and is a dict type
    
    return {"access_token": access_token, "token_type": "bearer"}
    