from fastapi import Depends, FastAPI, Body, Response, status, HTTPException, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db, engine
from sqlalchemy.orm import Session

router = APIRouter(
    prefix= "/posts",
    tags= ["Posts"]
)
#you will notice that the api calls are in the same pattern (ie starts with /posts/), so you can just mention them once as the prefix in the APIRouter class 
#so that you don't have to mention it repeatedly while creating endpoints
# router = APIRouter(prefix= "/posts"), now if you just write @app.get("/{id}"), FastAPI will understand that the user is calling the "/posts/{id}" endpoint

@router.get("/")
def get_posts(db : Session = Depends(get_db),user_id : int = Depends(oauth2.get_current_user)):
    # curr.execute('''SELECT * FROM posts''')
    # postsies = curr.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}



@router.get('/{id}', summary= "Get the details of a particular post")
#you can provide proper validation so that the parameter passed to the url is an integer using the id: str/int/bool
def particular_post(id: int, db : Session = Depends(get_db), user_id : int = Depends(oauth2.get_current_user)):
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


@router.post("/", status_code=status.HTTP_201_CREATED, response_model= schemas.Post) #the status code mentioned will show the 201 posted message if successfully posted
def create_post(post : schemas.PostCreate, db : Session = Depends(get_db), user_id : int = Depends(oauth2.get_current_user)): # we are going to add another dependancy which will force the user to login to create a post
# the dependency user_id of type integer will call the function called get_current_user and then call the verify_access_token function where we get the id and are storing the id in the variable "user_id"
    
    #trying to convert the pydantic model to python dictionary
    # curr.execute("""INSERT INTO posts ( title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #               (post.title , post.content ,post.published ) ) #remember the order matters
    # new_post = curr.fetchall()
    # but the above row will not be saved or committed into the table, we need to commit the changes (insertion of the post)
    # conn.commit() #this will push the changes to the table

    print(user_id)


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
@router.delete('/{id}', status_code= status.HTTP_204_NO_CONTENT)
def delete_post(id: int,  db : Session = Depends(get_db), user_id : int = Depends(oauth2.get_current_user)):
    # curr.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
    # deleted_post = curr.fetchone()
    # conn.commit()

    postie = db.query(models.Post).filter(models.Post.id == id)
    if postie.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No post found with the given id: {id}")
    
    postie.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.put("/{id}")
def update_post(id: int, post: schemas.PostBase,  db : Session = Depends(get_db), user_id : int = Depends(oauth2.get_current_user)):
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