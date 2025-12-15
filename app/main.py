import shutil
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from app.core.attendance import process_attendance
from app.core.database import db

app = FastAPI(title="Antigravity Attendance System")

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to Antigravity Attendance System found at /static/index.html"}

@app.get("/reload")
def reload_database():
    """Reloads the student database from disk."""
    db._load_students_from_disk()
    return {"message": f"Database reloaded. Total students: {len(db.students)}"}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save uploaded file temporarily
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Process attendance
        result = await process_attendance(file_location)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(file_location):
            os.remove(file_location)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
