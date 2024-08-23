from fastapi import Depends, FastAPI, Body, Response, status, HTTPException, APIRouter
from .. import models, schemas, utils
from ..database import get_db, engine
from sqlalchemy.orm import Session
#you will notice that you don't have access to the @app decorator object, so you should import APIRouter to route it instead of @app (replace @app with @router)

router = APIRouter(
    prefix= "/users", 
    tags=["Users"]
)

@router.post("/", status_code= status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user (user: schemas.UserCreate, db : Session = Depends(get_db)):

    #has the password which can be retrieved from user.password stored inside the user object
    hashed_password = utils.hash_password(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    #remember to return the new user or else u will get an error as to whose details should be shown as response to the user in the same format of the response model
    return new_user 


@router.get('/{id}', response_model=schemas.UserResponse)
def get_user ( id :int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} does not exist")
    
    return user