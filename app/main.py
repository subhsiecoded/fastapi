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


@app.get("/sqlalchemy") #just for testing purpose 
def test_post(db : Session = Depends(get_db)):
    posts = db.query(models.Post).all() #this will get all the entries in the posts table which is made by the Post class
    #also you can see the working of the above orm statement and how it varies from sql statements by doing the below mentioned steps.
    # posts = db.query(models.Post)
    # print(posts)
    #the above statement will print the following command:- SELECT posts.id AS posts_id, posts.title AS posts_title, posts.content AS posts_content, posts.published AS posts_published, posts.created_at AS posts_created_at 
    #FROM posts; THIS IS A REGULAR SQL STATEMENT, so basically ORM abstracts the sql away from you and uses python classes so that you don't have to know much about the sql statements  
    return {"data": posts}

@app.get("/posts")
def get_posts(db : Session = Depends(get_db)):
    # curr.execute('''SELECT * FROM posts''')
    # postsies = curr.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.get('/posts/{id}', summary= "Get the details of a particular post")
#you can provide proper validation so that the parameter passed to the url is an integer using the id: str/int/bool
def particular_post(id: int, db : Session = Depends(get_db)):
        #here the id is string always by default so we need to change it to int to make it match with the given id in the url
        # postie=get_post(id)
        #let give proper error if post is not found

        # curr.execute("""SELECT * FROM posts WHERE id = %s""",(str(id)))
        # postie=curr.fetchone()

        postie = db.query(models.Post).filter(models.Post.id == id ).all() #you can use .all() or .first()
        if not postie:
            #response.status_code = 404  this is hard coded, you can rather use the status from fastapi library
            #response.status_code = status.HTTP_404_NOT_FOUND
            # we can also raise HTTP exception, which is in the fastapi module
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f'there is no post with the id {id}')
        return {"data" : postie} 

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model= schemas.Post) #the status code mentioned will show the 201 posted message if successfully posted
def create_post(post : schemas.PostCreate, db : Session = Depends(get_db)):
    #trying to convert the pydantic model to python dictionary
    # curr.execute("""INSERT INTO posts ( title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #               (post.title , post.content ,post.published ) ) #remember the order matters
    # new_post = curr.fetchall()
    # but the above row will not be saved or committed into the table, we need to commit the changes (insertion of the post)
    # conn.commit() #this will push the changes to the table



    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    # in the above statement, we need to write the fields as post.(field) the number of times as the number if fields available, so what we can do is:-
    # we need to unpack the dictionary    
    
    new_post = models.Post(**post.dict())

    db.add(new_post) # adds the newly created post to the database

    # we need to commit the above changes
    db.commit()
    db.refresh(new_post) #returns the entire rows of the new post created 
    #remember to return the new post or else u will get an error as to which particular posts's details should be shown as response to the user in the same format of the response model
    return new_post

#'/posts/latest' will give error as there is another identical link above ie the /posts/{id} and is looking for the id to be an integer value
#FastAPI runs from top to bottom
'''"msg": "Input should be a valid integer, unable to parse string as an integer",
            "input": "latest"'''
#you can solve this issue by moving this above the other similar link or can change the url

#deleting the post using the delete method 
#make sure to add the status code for deleting a post that is 204
@app.delete('/posts/{id}', status_code= status.HTTP_204_NO_CONTENT)
def delete_post(id: int,  db : Session = Depends(get_db)):
    # curr.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
    # deleted_post = curr.fetchone()
    # conn.commit()

    postie = db.query(models.Post).filter(models.Post.id == id)
    if postie.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No post found with the given id: {id}")
    
    postie.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: schemas.PostBase,  db : Session = Depends(get_db)):
    # curr.execute(
    #     """UPDATE posts SET title = %s, content = %s WHERE id = %s RETURNING *""",
    #     (post.title, post.content, str(id))
    # )
    # conn.commit()
    # edited_post = curr.fetchone()


    edited_post_query = db.query(models.Post).filter(models.Post.id == id)
    
    edited_post = edited_post_query.first()

    if edited_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} not found.")

    edited_post_query.update(post.dict(), synchronize_session=False) #post.dict() will change the body to python dictionary
    db.commit()

    return {"edited_post": edited_post_query.first()}


@app.post("/users", status_code= status.HTTP_201_CREATED, response_model=schemas.UserResponse)
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
