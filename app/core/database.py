import os
import face_recognition
import numpy as np
from typing import List, Dict, Any, Optional

# Global database instance
db = None

class StudentDatabase:
    def __init__(self, data_dir: str = "app/data/students"):
        self.students = []
        self.data_dir = data_dir
        self._load_students_from_disk()

    def _load_students_from_disk(self):
        """
        Loads student images from the data directory.
        Expected filename format: "Name_RollNo.jpg" (or png, jpeg)
        Puts them into the in-memory database with their face encodings.
        """
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
            print(f"Created data directory: {self.data_dir}")
            return

        # Clear existing data to avoid duplicates on reload
        self.students = []
        print(f"Loading students from {self.data_dir}...")
        
        valid_extensions = ('.jpg', '.jpeg', '.png')
        count = 0
        
        for filename in os.listdir(self.data_dir):
            if not filename.lower().endswith(valid_extensions):
                continue
                
            # Parse filename: Name_RollNo.jpg
            name_part = os.path.splitext(filename)[0]
            
            # Simple parsing strategy: split by last underscore
            # Example: "John Doe_R001" -> Name: "John Doe", Roll: "R001"
            if '_' in name_part:
                *name_tokens, roll_no = name_part.rsplit('_', 1)
                name = "_".join(name_tokens) # Join back if name had underscores, though risky.
                # Better: "John Doe_R001" -> name="John Doe", roll="R001"
            else:
                # Fallback if no underscore
                name = name_part
                roll_no = "Unknown"

            file_path = os.path.join(self.data_dir, filename)
            
            try:
                image = face_recognition.load_image_file(file_path)
                encodings = face_recognition.face_encodings(image)
                
                if len(encodings) > 0:
                    # We assume one face per registration photo
                    self.register_student(name, roll_no, encodings[0])
                    count += 1
                    print(f"Registered: {name} ({roll_no})")
                else:
                    print(f"Warning: No face found in {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")

        print(f"Total students registered: {count}")
        if count == 0:
             print("No students found. Using mock data for demonstration.")
             self._seed_mock_data()

    def _seed_mock_data(self):
        # Fallback mock data if no images provided
        self.register_student("Alice Smith", "R001")
        self.register_student("Bob Johnson", "R002")
        self.register_student("Charlie Brown", "R003")

    def register_student(self, name: str, roll_no: str, embedding: Optional[List[float]] = None):
        if embedding is None:
            # Random embedding for mock only
            embedding = np.random.rand(128).tolist()
            
        self.students.append({
            "name": name,
            "roll_no": roll_no,
            "embedding": np.array(embedding)
        })

    def get_all_students(self) -> List[Dict[str, Any]]:
        return self.students

# Initialize global instance
db = StudentDatabase()
