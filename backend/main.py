from typing import Union
import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator

app = FastAPI()

# Define a list of allowed origins (the domains your frontend is hosted on)
origins = ["http://localhost:3000"]

class Item(BaseModel):
    x: str

    # Optional: Add a validator to ensure the input is a valid YouTube link
    @validator('x')
    def validate_youtube_link(cls, v):
        youtube_link_regex = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        if not re.match(youtube_link_regex, v):
            raise ValueError('Invalid YouTube link')
        return v

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
def handle_youtube_link(item: Item):
    # Assuming you just want to acknowledge the receipt of the YouTube link for now
    print(item.x)  # Print the YouTube link to the console (or handle it as needed)
    return {"message": "YouTube link received successfully!"}
