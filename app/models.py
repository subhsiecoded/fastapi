#every model defines a table in the database
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import engine, Base
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

class Post(Base):
    __tablename__= "posts" #define the name of the table 

    id = Column(Integer, nullable = False, primary_key=True)
    title = Column(String, nullable = False)
    content = Column(String, nullable= False)
    published = Column(Boolean, server_default="True" , nullable = False) #there is a default value for the published column 
    #which will be set when the column is left empty
    #also, note you need to use "server_default=" parameter in order to define the default value to be given by the postgresql server
    created_at = Column(TIMESTAMP(timezone=True), nullable= False, server_default= text('now()'))

    #let's create a foreign key for the posts table that refers the user id from the users table (users.id) so that each post will be asssociated with an user
    owner_id= Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable = False) 
    #remember the first argument will take the `tablename.column` you are referencing and not the class name (not Users())

    # you can also make relaitonships from one model class to other
    owner = relationship("User") # remember we are not referencing the table, but the class User
    # when we fetch a post, it's going to return an "owner" property which will define the relationship with the user
    #next, update the schema


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, nullable = False, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable= False, server_default= text('now()'))