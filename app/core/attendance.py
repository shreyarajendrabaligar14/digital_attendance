import face_recognition
import numpy as np
from typing import List, Dict, Any
from .database import db

MATCH_THRESHOLD = 0.5 # Lower is stricter. 0.6 is typical default. User asked for 80% confidence? 
# "Accept a match only if confidence >= 80%"
# In distance terms, Euclidean distance of 0.6 is the cutoff. 
# Confidence is roughly (1 - distance). So distance <= 0.2? That's very strict.
# Let's align with common practices:
# 0.6 distance is typical match. 
# If they want "80% confidence", we can interpret that mapping distance to confidence.
# For now, I will use a conservative distance threshold, e.g., 0.5.

def calculate_confidence(face_distance: float, face_match_threshold: float = 0.6) -> float:
    range_val = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range_val * 2.0)

    if face_distance > face_match_threshold:
        return round(linear_val * 100, 2)
    else:
        value = (linear_val + ((1.0 - linear_val) * np.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return round(value, 2)

async def process_attendance(image_file_path: str) -> Dict[str, Any]:
    # 1. Load the uploaded image
    image = face_recognition.load_image_file(image_file_path)
    
    # 2. Detect Faces
    # using 'hog' is faster, 'cnn' is more accurate but requires GPU
    # 3. Face Recognition & 4. Match
    # Upsample to detect faces in group photos better
    # Note: Increasing upsample slows it down but detects smaller faces
    face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=2, model="hog")
    face_encodings = face_recognition.face_encodings(image, face_locations)
    
    # Get all registered students
    all_students = db.get_all_students()
    known_face_encodings = [s["embedding"] for s in all_students]
    known_face_names = [s["name"] for s in all_students]
    known_face_rolls = [s["roll_no"] for s in all_students]

    found_present_indices = set()
    present_students_list = []
    
    unknown_count = 0

    for face_encoding in face_encodings:
        # If no known students, all faces are unknown
        if len(known_face_encodings) == 0:
            unknown_count += 1
            continue

        # Compare face with registered students
        distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        
        # Find best match
        best_match_index = np.argmin(distances)
        min_distance = distances[best_match_index]
        
        # Threshold check (0.5 is strict/safe)
        if min_distance <= 0.5:
            # If this student hasn't been marked present yet
            if best_match_index not in found_present_indices:
                confidence = calculate_confidence(min_distance)
                
                found_present_indices.add(best_match_index)
                present_students_list.append({
                    "name": known_face_names[best_match_index],
                    "roll_no": known_face_rolls[best_match_index],
                    "match_confidence": confidence
                })
            else:
                # This student was already found. 
                # This face is either a duplicate detection or a false positive match.
                # We do NOT count it as unknown, as it matched someone.
                pass
        else:
            # Face did not match any registered student significantly
            unknown_count += 1

    # 5. Attendance Decision
    absent_students_list = []
    for idx, student in enumerate(all_students):
        if idx not in found_present_indices:
            absent_students_list.append({
                "name": student["name"],
                "roll_no": student["roll_no"]
            })

    # 6. Summary
    result = {
        "total_students": len(all_students),
        "present_count": len(present_students_list),
        "absent_count": len(absent_students_list),
        "present_students": present_students_list,
        "absent_students": absent_students_list,
        "unknown_faces_detected": unknown_count
    }
    
    return result
