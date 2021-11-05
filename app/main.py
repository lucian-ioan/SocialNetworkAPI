import psycopg2

from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.param_functions import Body

from pydantic import BaseModel

from typing import Optional
from random import randrange

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

try:
    with open("credentials.txt") as f:
        lines = f.readlines()
        user, password = lines[0].strip(), lines[1].strip()

    conn = psycopg2.connect(host="localhost", database="SocialNetwork", 
                            user=user, password=password,
                            cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Database connection was succesful")
except Exception as err:
    print("Database connection failed")
    print("Error: ", err)


@app.get("/")
def root():
    return {"message": "Hello Stefan"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", 
                  (post.title, post.content, post.published))

    new_post = cursor.fetchone()
    conn.commit()
    
    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    post = cursor.fetchone()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} was not found")

    return {"post_detail": post}

@app.delete("/posts/{id}")
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} was not found")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} was not found")

    return {"data": updated_post}
