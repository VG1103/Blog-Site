import mysql.connector
from fastapi import FastAPI,Form,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles


app = FastAPI()
templates = Jinja2Templates(directory="HTML")
app.mount("/CSS", StaticFiles(directory="CSS"), name="static")

db = mysql.connector.connect(
  host = "localhost",
  user="root",
  password="1234",
  database="blog_db"

)
cursor = db.cursor()
print("Database connected")

cursor.execute("""
               CREATE TABLE IF NOT EXISTS posts (
               id INT AUTO_INCREMENT PRIMARY KEY,
               title VARCHAR(255) NOT NULL,
               content TEXT NOT NULL)
               """)
db.commit()

@app.get("/",response_class = HTMLResponse)
async def read_posts(request: Request):
  cursor.execute("SELECT * FROM posts")
  posts = cursor.fetchall()
  return templates.TemplateResponse("index.html",{"request":request,"posts":posts})

@app.get("/create_post", response_class = HTMLResponse)
async def create_post_page(request:Request):
  return templates.TemplateResponse("create_post.html",{"request":request})

@app.post("/create_post",response_class=HTMLResponse)
async def create_post(title: str = Form(...),content: str = Form(...)):
  cursor.execute("INSERT INTO posts (title,content) VALUES (%s,%s)", (title,content))
  db.commit()
  return RedirectResponse(url="/", status_code=303)

@app.get("/post/{post_id}",response_class=HTMLResponse)
async def read_post(request: Request,post_id: int):
  cursor.execute("SELECT * FROM posts WHERE id = %s",(post_id,))
  post = cursor.fetchone()
  if not post:
    raise HTTPException(status_code = 404, detail="Post not found")
  return templates.TemplateResponse("post.html",{"request":request,"post":post})

@app.get("/edit/{post_id}",response_class=HTMLResponse)
async def edit_post_page(request: Request,post_id:int):
  cursor.execute("SELECT * FROM posts WHERE id = %s",(post_id,))
  post = cursor.fetchone()
  if not post:
    raise HTTPException(status_code=404, detail="Post not found")
  return templates.TemplateResponse("edit.html",{"request": request,"post":post})

@app.post("/update_post/{post_id}",response_class=RedirectResponse)
async def update_post(post_id: int,title: str = Form(...),content: str = Form(...)):
  cursor.execute("UPDATE posts SET title = %s,content = %s WHERE id = %s",(title,content,post_id))
  db.commit()
  return RedirectResponse(url="/", status_code=303)

@app.post("/delete/{post_id}",response_class=RedirectResponse)
async def delete_post(post_id: int):
  cursor.execute("DELETE FROM posts WHERE id =%s", (post_id,))
  db.commit()
  return RedirectResponse(url="/", status_code= 303)


  
