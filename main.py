from fastapi import FastAPI, HTTPException, Query
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from typing import List, Any, Optional
from typing import List, Any, Optional
from datetime import datetime
import os
import bcrypt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://rameswarreddy78:Oxygen0816@cluster0.c1dizfg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
client = MongoClient(MONGODB_URI)
db = client["form_table_db"]
collection = db["form_data"]
user_collection = db["users"]

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
    createdAt: str = ""  # ISO date string


class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    createdAt: Optional[str] = ""

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Signup route
@app.post("/signup")
def signup(user: User):
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered.")
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    user_dict = user.dict()
    user_dict["password"] = hashed_pw.decode('utf-8')
    user_dict["createdAt"] = datetime.utcnow().isoformat()
    result = user_collection.insert_one(user_dict)
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to create user.")
    return {"message": "Signup successful", "user_id": str(result.inserted_id)}

# Login route
@app.post("/login")
def login(request: LoginRequest):
    user = user_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not bcrypt.checkpw(request.password.encode('utf-8'), user["password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    return {"message": "Login successful", "name": user["name"], "email": user["email"]}

@app.post("/upload")
def upload_data(form_data: FormData):
    form_data.createdAt = datetime.utcnow().isoformat()
    result = collection.insert_one(form_data.dict())
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to insert data.")
    return {"inserted_id": str(result.inserted_id)}

@app.get("/fetch", response_model=List[Any])
def fetch_data(
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}}
        ]
    
    if start_date and end_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            query["createdAt"] = {
                "$gte": start_dt.isoformat(),
                "$lte": end_dt.isoformat()
            }
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    
    return list(collection.find(query, {"_id": 0}))

@app.put("/update/{phone}")
def update_data(phone: str, updated_data: FormData):
    result = collection.update_one({"phone": phone}, {"$set": updated_data.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Updated successfully"}

@app.delete("/delete/{phone}")
def delete_data(phone: str):
    result = collection.delete_one({"phone": phone})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Deleted successfully"}
