from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import os
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware # Important for React Native to connect

# Initialize the FastAPI application
app = FastAPI()

# --- CORS Configuration ---
# This is crucial for your React Native app to be able to connect to this API.
# In development, you might allow all origins. In production, restrict it to your app's domain.
origins = [
    "*", # Allows all origins for development/testing (NOT recommended for production)
    # "http://localhost:8081",  # Example for Expo development server
    # "exp://your-expo-app-id.exp.direct:80", # Example for Expo Go (can vary)
    # "https://your-production-app.com", # Your production app's domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)


FILE_PATH = os.path.join(os.path.dirname(__file__), "reminders.txt")




class TimeDetailEntry(BaseModel):
    time: str = "" 
    detail: str = "" 

# Pydantic model forhe request body when updating entries
# This expects a list of strings, e.g., ["08:00|Morning meeting", "12:30|Lunch break", ...]
class UpdateEntriesRequest(BaseModel):
    entries: List[str] = Field(..., min_items=6, max_items=6) # Expects exactly 6 entries

# Pydantic model for the response body when reading entries
# This will return a list of objects, e.g., [{"time": "08:00", "detail": "Morning meeting"}, ...]
class ReadEntriesResponse(BaseModel):
    entries: List[TimeDetailEntry]

# --- API Endpoints ---

@app.get("/read-entries", response_model=ReadEntriesResponse)
async def read_entries():
    """
    Reads the time and detail entries from entries.txt and returns them as a list of objects.
    Each line in entries.txt is expected to be in "HH:MM|text" format.
    """
    entries_list: List[TimeDetailEntry] = []
    
    if not os.path.exists(FILE_PATH):
        # If file doesn't exist, return 6 empty entries
        return JSONResponse(content={"entries": [TimeDetailEntry().dict() for _ in range(6)]})
    
    try:
        with open(FILE_PATH, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if "|" in line:
                    parts = line.split("|", 1) # Split only on the first '|'
                    time_str = parts[0].strip()
                    detail_str = parts[1].strip() if len(parts) > 1 else ""
                    entries_list.append(TimeDetailEntry(time=time_str, detail=detail_str))
                else:
                    # Handle lines that might not conform to the HH:MM|text format gracefully
                    entries_list.append(TimeDetailEntry(time="", detail=line))

        # Ensure exactly 6 entries are always returned
        while len(entries_list) < 6:
            entries_list.append(TimeDetailEntry(time="", detail=""))
        
        return JSONResponse(content={"entries": [entry.dict() for entry in entries_list[:6]]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read entries: {e}")

@app.post("/update-entries")
async def update_entries(request: UpdateEntriesRequest):
    """
    Updates the time and detail entries in entries.txt with the provided list of strings.
    Each string in the list should be in "HH:MM|text" format.
    """
    try:
        with open(FILE_PATH, "w") as f:
            for entry_string in request.entries:
                f.write(entry_string + "\n") # Write each entry on a new line
        return JSONResponse(content={"message": "Entries updated successfully!"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update entries: {e}")

# Optional: Root endpoint for basic health check
@app.get("/")
async def root():
    return {"message": "FastAPI server is running!"}

# --- Old Endpoints (Optional: Remove if not needed anymore) ---
# Keeping them for now in case you still need to interact with the old number.txt
# If you remove these, also remove the 'UpdateNumberRequest' model and 'number.txt' FILE_PATH if not used.

OLD_NUMBER_FILE_PATH = os.path.join(os.path.dirname(__file__), "number.txt")

class UpdateNumberRequest(BaseModel):
    newNumber: str

@app.get("/read-number")
async def read_number():
    """
    Reads the phone number from number.txt and returns it.
    """
    if not os.path.exists(OLD_NUMBER_FILE_PATH):
        raise HTTPException(status_code=404, detail="number.txt not found.")
        
    try:
        with open(OLD_NUMBER_FILE_PATH, "r") as f:
            number = f.read().strip()
        return JSONResponse(content={"number": number})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read number: {e}")

@app.post("/update-number")
async def update_number(request: UpdateNumberRequest):
    """
    Updates the phone number in number.txt with the provided newNumber.
    """
    try:
        with open(OLD_NUMBER_FILE_PATH, "w") as f:
            f.write(request.newNumber)
        return JSONResponse(content={"message": "Number updated successfully!"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update number: {e}")
