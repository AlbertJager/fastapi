from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor 
import time

pswd = "blabla"
app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(database="fastapi", host="localhost", user="postgres", password=pswd, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Success!")
        break
    except Exception as e:
        print("Failed!", e)
        time.sleep(3)

    
# def find_index(id):
#     for index, post in enumerate(posts):
#         if post.get("id")==id:
#             return index
#     else:
#         raise HTTPException(status_code=404, detail=f"Post with id {id} does not exist")                


class Post(BaseModel):
    # id: int
    title: str
    content: str
    published: bool = True
    rating: float | None = None


class UpdatePost(BaseModel):
    title: str | None = None
    content: str | None = None
    published: bool | None  = None
    rating: float | None = None
    

    
@app.get("/") 
def root():
    return "root"


#CREATE
@app.post("/posts", status_code = status.HTTP_201_CREATED)
def create_posts(new_post: Post):  # в эту переменную запишется значение из тела запроса, а пишем : Post для валидации и чтобы код понимал откуда брать данные
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (new_post.title, new_post.content, new_post.published))
    post = cursor.fetchone()
    conn.commit()
    return post

#READ
@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return posts

#READ
@app.get("/posts/{id}")
def get_post(id: int):  # тут мы говорим, что тип данных должен быть интом 
    cursor.execute("""SELECT * FROM posts where id = %s""", (id, ))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    else:   
        return result
    

#put    
@app.put("/posts/{id}", status_code=status.HTTP_200_OK)
def put_post(id: int, update_post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (update_post.title, update_post.content, update_post.published, id))
    updated_post = cursor.fetchone()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    else:
        conn.commit()
        return updated_post    
        
    
#patch
@app.patch("/posts/{id}", status_code=status.HTTP_200_OK)
def patch_post(id: int, update_post: UpdatePost):
    for key, value in update_post.model_dump().items():
        cursor.execute("UPDATE posts SET %s=%s WHERE id = %s", (key, value, id))
        conn.commit()
    
    
#DELETE
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_handler(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING title """, (id, ))
    deleted_post = cursor.fetchone()
    if not deleted_post:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    conn.commit()