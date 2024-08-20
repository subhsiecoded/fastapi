# define your schemas and pydantic objects here, and import the modesl to other files 
from pydantic import BaseModel
from datetime import datetime
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True # this is an optional field for the request. If not defined by the user, it will be giving the default value (in this case, it is true)
    #now lets see another optional field using typing module 


# you can also restructure the pydantic models for functions like creation and updation
# this will help in making the user send only one field in case of updation, like for example if the user is allowed to only pass the "published" attribute

# ANOTHER METHOD IS creating a class like Post (call it PostBase) and then extending the PostBase class created.
# so for CreatePost, you will just write pass as it will take the same fields as the PostBase class
# and for UpdatePost which will also extend PostBase, you can just pass the fields necessary to be passed by the user while updating the post

class PostCreate(PostBase):
    pass




class Post(BaseModel):
    #you are defining the fields you want to show the user in the response, you can add id and created_at too
    id:int
    created_at:datetime




    #if you are setting the class as a response model, you will get an error as the response will not be a valid dict 
    # so you need to add another class called Config() where you need to set the orm_mode to True. 
    # Pydantic's orm_mode will tell the Pydantic model to read the data even if it is not a dict, but an ORM model (or any other arbitrary object with attributes).
    class Config():
        orm_mode = True