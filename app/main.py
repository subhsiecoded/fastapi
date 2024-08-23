from fastapi import Depends, FastAPI, Body, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional
import random
import time
import psycopg2 as pg
from psycopg2.extras import RealDictCursor #we need this to load the column names, without this only the values will be rendered
from .database import engine, get_db
from . import models, schemas, utils
from sqlalchemy.orm import Session
from .routers import post, user, auth

models.Base.metadata.create_all(bind=engine) #this statement creates a table and what it does is it looks for a table if existing with the name mentioned in the model, if there's no such table, it will make one. 
#so even after you change the code in the models.py, the table will remain unaffected.

app=FastAPI()


posts= [{'id':1, 'title': 'this is the first post', 'content': 'abcd'}, {'id': 2, 'title':'this is the second post', 'content': 'subh'}]
    

while True:
    try: 
        conn = pg.connect(host= "localhost", user = "postgres", database="fastapi", password = "root@!5702", cursor_factory=RealDictCursor)
        curr= conn.cursor()
        print("connection successful")
        break

    except Exception as error:
        print("Connection to the database failed")
        print("error:", error)
        time.sleep(2) #this will reload every 2 seconds in case of error connecting

def get_post(id):
    for p in posts:
        if p['id']==id:
            return p


def find_index_post(id):
    for i,p in enumerate(posts):
        if p['id']==id:
            return i

#you need to include the routers for the FastAPI app
app.include_router(post.router)
#the above statement will check the router in the post.py file and then the request will go there
app.include_router(user.router) # we are accessing the router object from the user file which will just import the routes (API endpoints)
app.include_router(auth.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/trial") #just for testing purpose 
def test_post(db : Session = Depends(get_db)):
    posts = db.query(models.Post).all() #this will get all the entries in the posts table which is made by the Post class
    #also you can see the working of the above orm statement and how it varies from sql statements by doing the below mentioned steps.
    # posts = db.query(models.Post)
    # print(posts)
    #the above statement will print the following command:- SELECT posts.id AS posts_id, posts.title AS posts_title, posts.content AS posts_content, posts.published AS posts_published, posts.created_at AS posts_created_at 
    #FROM posts; THIS IS A REGULAR SQL STATEMENT, so basically ORM abstracts the sql away from you and uses python classes so that you don't have to know much about the sql statements  
    return {"data": posts}


