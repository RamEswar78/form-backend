from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List, Any
import os

app = FastAPI()

# Allow CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your React app's URL later
    allow_credentials=True,
    allow_methods=["*"],  # This enables OPTIONS requests too
    allow_headers=["*"],
)

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://rameswarreddy78:Oxygen0816@cluster0.c1dizfg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
client = MongoClient(MONGODB_URI)
db = client["form_table_db"]
collection = db["form_data"]

class FormData(BaseModel):
    name: str
    email: str
    phone: str
    sipLumpsum: str
    healthInsurance: str
    termInsurance: str
    twoWheeler: str
    fourWheeler: str
    healthInsuranceExpiry: str = ""
    termInsuranceExpiry: str = ""
    twoWInsuranceExpiry: str = ""
    fourWInsuranceExpiry: str = ""
    referredBy: str = ""

@app.post("/upload")
def upload_data(form_data: FormData):
    result = collection.insert_one(form_data.dict())
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to insert data.")
    return {"inserted_id": str(result.inserted_id)}

@app.get("/fetch", response_model=List[Any])
def fetch_data():
    return list(collection.find({}, {"_id": 0}))
