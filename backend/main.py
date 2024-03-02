from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

app = FastAPI()

# Define a list of allowed origins (the domains your frontend is hosted on)
# You can use ["*"] to allow all origins
origins = [
    "http://localhost:3000",
]

class item(BaseModel):
    x: str

# Add CORSMiddleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies to be included in requests
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/test")
def Sanity(item: item):
    print(item.x)
    if item.x.isdigit():
        return {"message": str([i ** 2 for i in range(int(item.x))])}
    return {"message": "come on, give a number"}