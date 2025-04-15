import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import os
import datetime
from dataclass import Author, Publication, Education, Examination, PersonalData, Document


class MetadataEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Ground Truther")
        self.root.geometry("1200x800")
        
        # Set up logger
        import logging
        self.logger = logging.getLogger(__name__)
        
        self.current_image_path = None
        self.current_json_path = None
        self.json_data = None
        self.images_in_folder = []
        self.current_image_index = -1
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout - split into left (image) and right (metadata form)
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame for image display
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Image canvas with scrollbars
        self.image_canvas = tk.Canvas(left_frame, bg="white")
        h_scrollbar = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=self.image_canvas.xview)
        v_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.image_canvas.yview)
        
        self.image_canvas.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.image_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right frame for metadata form
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        # File selection buttons
        file_frame = ttk.Frame(right_frame)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(file_frame, text="Open Image", command=self.open_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Open JSON", command=self.open_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Save JSON", command=self.save_json).pack(side=tk.LEFT, padx=5)
        
        # Navigation buttons
        nav_frame = ttk.Frame(right_frame)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(nav_frame, text="Previous Image", command=self.previous_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Next Image", command=self.next_image).pack(side=tk.LEFT, padx=5)
        
        # Counter display 
        self.counter_label = ttk.Label(nav_frame, text="Image 0 of 0")
        self.counter_label.pack(side=tk.LEFT, padx=10)
        
        # Display file names
        self.file_info_frame = ttk.LabelFrame(right_frame, text="Current Files")
        self.file_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.image_label = ttk.Label(self.file_info_frame, text="Image: None")
        self.image_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.json_label = ttk.Label(self.file_info_frame, text="JSON: None")
        self.json_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Metadata form
        self.form_frame = ttk.LabelFrame(right_frame, text="Metadata")
        self.form_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create scrollable frame for the form
        form_canvas = tk.Canvas(self.form_frame)
        form_scrollbar = ttk.Scrollbar(self.form_frame, orient=tk.VERTICAL, command=form_canvas.yview)
        
        self.scrollable_frame = ttk.Frame(form_canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: form_canvas.configure(scrollregion=form_canvas.bbox("all")))
        
        form_canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        form_canvas.configure(yscrollcommand=form_scrollbar.set)
        
        form_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        form_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Form elements will be dynamically created based on JSON structure
        self.form_elements = {}
        
    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        
        if file_path:
            self.load_image(file_path)
            
    def update_images_in_folder(self):
        """Find all image files in the same folder as the current image."""
        if not self.current_image_path:
            self.logger.info("No current image, cannot update folder listing")
            return
            
        folder = os.path.dirname(self.current_image_path)
        self.images_in_folder = []
        
        self.logger.info(f"Scanning folder: {folder}")
        
        # Get all image files in the folder
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        for file in os.listdir(folder):
            if file.lower().endswith(image_extensions):
                full_path = os.path.join(folder, file)
                self.images_in_folder.append(full_path)
        
        # Sort alphabetically
        self.images_in_folder.sort()
        
        self.logger.info(f"Found {len(self.images_in_folder)} images in folder")
        
        # Find current image index
        try:
            # Normalize paths for comparison
            current_path = os.path.normpath(os.path.abspath(self.current_image_path))
            normalized_paths = [os.path.normpath(os.path.abspath(p)) for p in self.images_in_folder]
            
            self.logger.debug(f"Current path: {current_path}")
            self.logger.debug(f"Available paths: {normalized_paths}")
            
            self.current_image_index = normalized_paths.index(current_path)
            self.logger.info(f"Current image index: {self.current_image_index}")
        except ValueError:
            self.logger.warning(f"Current image {self.current_image_path} not found in folder list")
            self.current_image_index = -1
            
        # Update counter label
        self.update_counter_label()
        
    def update_counter_label(self):
        """Update the image counter label."""
        if not self.images_in_folder:
            self.counter_label.config(text="Image 0 of 0")
        else:
            self.counter_label.config(text=f"Image {self.current_image_index + 1} of {len(self.images_in_folder)}")
            
    def load_image(self, file_path):
        """Load an image file and its associated JSON metadata."""
        self.logger.info(f"Loading image: {file_path}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            self.logger.error(f"Image file not found: {file_path}")
            messagebox.showerror("Error", f"Image file not found: {file_path}")
            return
            
        self.current_image_path = file_path
        self.image_label.config(text=f"Image: {os.path.basename(file_path)}")
        self.display_image()
        
        # Find all images in the folder for navigation
        self.update_images_in_folder()
        
        # Try to find matching JSON file
        base_name = os.path.splitext(file_path)[0]
        possible_json = f"request_T66_{os.path.basename(base_name)}.json"
        possible_json_path = os.path.join(os.path.dirname(file_path), possible_json)
        
        self.logger.info(f"Looking for JSON file: {possible_json_path}")
        
        if os.path.exists(possible_json_path):
            self.current_json_path = possible_json_path
            self.json_label.config(text=f"JSON: {os.path.basename(possible_json_path)}")
            self.load_json()
        else:
            # Clear the form if no JSON found
            self.logger.warning(f"No JSON file found for this image")
            self.current_json_path = None
            self.json_label.config(text="JSON: None")
            
            # Clear existing form elements
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            self.form_elements = {}
    
    def open_json(self):
        file_path = filedialog.askopenfilename(
            title="Select JSON",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            self.current_json_path = file_path
            self.json_label.config(text=f"JSON: {os.path.basename(file_path)}")
            self.load_json()
            
            # Try to find matching image file
            json_basename = os.path.basename(file_path)
            if json_basename.startswith("request_T66_"):
                image_name = json_basename.replace("request_T66_", "").replace(".json", "")
                possible_image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
                
                for ext in possible_image_extensions:
                    possible_image_path = os.path.join(os.path.dirname(file_path), image_name + ext)
                    if os.path.exists(possible_image_path):
                        self.current_image_path = possible_image_path
                        self.image_label.config(text=f"Image: {os.path.basename(possible_image_path)}")
                        self.display_image()
                        
                        # Find all images in the folder for navigation
                        self.update_images_in_folder()
                        break
    
    def display_image(self):
        if not self.current_image_path:
            return
            
        # Clear the canvas
        self.image_canvas.delete("all")
        
        # Load and display the image
        try:
            image = Image.open(self.current_image_path)
            self.tk_image = ImageTk.PhotoImage(image)
            
            # Configure canvas scrollregion
            self.image_canvas.config(scrollregion=(0, 0, image.width, image.height))
            
            # Display the image
            self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def load_json(self):
        """Load JSON data from file and create form elements."""
        if not self.current_json_path:
            return
            
        try:
            with open(self.current_json_path, 'r') as f:
                self.json_data = json.load(f)
            
            # Ensure expected structure exists
            if "response_text" not in self.json_data:
                self.json_data["response_text"] = {}
                
            # Initialize author structure if needed
            if "author" not in self.json_data["response_text"]:
                self.json_data["response_text"]["author"] = {
                    "first_name": "",
                    "last_name": ""
                }
            
            # Initialize personal_data structure if needed
            if "personal_data" not in self.json_data["response_text"]:
                self.json_data["response_text"]["personal_data"] = None
                
            # Clear existing form elements
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
                
            self.form_elements = {}
            
            # Create form based on JSON structure
            self.create_form(self.json_data, "", self.scrollable_frame)
            
            # Debug information
            self.logger.info("Loaded JSON data: %s", self.json_data)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.logger.error("Failed to load JSON: %s", str(e), exc_info=True)
            messagebox.showerror("Error", f"Failed to load JSON: {str(e)}")
    
    def create_form(self, data, path, parent_frame):
        """
        Create form elements for the JSON data structure.
        
        Args:
            data: The current JSON data value to create form elements for
            path: The string representation of the current path in the JSON structure
            parent_frame: The parent tkinter frame to add elements to
        """
        if isinstance(data, dict):
            # Create a frame for this dictionary
            display_key = path.split('.')[-1] if path else ""
            
            if display_key:
                frame = ttk.LabelFrame(parent_frame, text=display_key)
                frame.pack(fill=tk.X, padx=5, pady=5, anchor=tk.W)
            else:
                frame = parent_frame
                
            # Process each key-value pair
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                self.create_form(value, new_path, frame)
                
        elif isinstance(data, list):
            # Create a frame for this list
            display_key = path.split('.')[-1] if path else ""
            frame = ttk.LabelFrame(parent_frame, text=display_key)
            frame.pack(fill=tk.X, padx=5, pady=5, anchor=tk.W)
            
            # Special handling for author
            if path.endswith("author") and not any(s in path for s in ["[", "]"]):
                # This is the author object in response_text.author
                # Create a frame for the author fields
                author_frame = ttk.Frame(frame)
                author_frame.pack(fill=tk.X, padx=5, pady=5)
                
                # Create fields for first and last name
                first_name_frame = ttk.Frame(author_frame)
                first_name_frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(first_name_frame, text="First Name:").pack(side=tk.LEFT, padx=5)
                first_name_var = tk.StringVar(value=data.get("first_name", "") if isinstance(data, dict) else "")
                first_name_entry = ttk.Entry(first_name_frame, textvariable=first_name_var, width=40)
                first_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                last_name_frame = ttk.Frame(author_frame)
                last_name_frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(last_name_frame, text="Last Name:").pack(side=tk.LEFT, padx=5)
                last_name_var = tk.StringVar(value=data.get("last_name", "") if isinstance(data, dict) else "")
                last_name_entry = ttk.Entry(last_name_frame, textvariable=last_name_var, width=40)
                last_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                # Save the variables
                self.form_elements[f"{path}.first_name"] = {"type": "string", "var": first_name_var, "path": f"{path}.first_name"}
                self.form_elements[f"{path}.last_name"] = {"type": "string", "var": last_name_var, "path": f"{path}.last_name"}
                
                # Special handling for custom author object
                self.form_elements[path] = {"type": "author_object", "path": path, 
                                           "first_name": first_name_var, "last_name": last_name_var}
            # Special handling for university education list
            elif path.endswith("university") and isinstance(data, list):
                university_values = data if data and data is not None else []
                
                # Add a label to make it clearer
                ttk.Label(frame, text="University Education (add one per line):").pack(anchor=tk.W, padx=5, pady=2)
                
                # Container for university entries
                university_container = ttk.Frame(frame)
                university_container.pack(fill=tk.X, padx=5, pady=5)
                
                # Keep track of university entries
                self.university_entries = []
                
                # Function to add university entry
                def add_university_entry(value=""):
                    entry_frame = ttk.Frame(university_container)
                    entry_frame.pack(fill=tk.X, pady=2)
                    
                    entry = ttk.Entry(entry_frame, width=40)
                    entry.pack(side=tk.LEFT, padx=2)
                    entry.insert(0, value)
                    
                    def remove_entry():
                        self.university_entries.remove(entry)
                        entry_frame.destroy()
                    
                    remove_btn = ttk.Button(entry_frame, text="Remove", command=remove_entry)
                    remove_btn.pack(side=tk.LEFT, padx=2)
                    
                    self.university_entries.append(entry)
                    return entry
                
                # Add existing university entries
                for univ in university_values:
                    if univ: # Skip None or empty strings
                        add_university_entry(univ)
                
                # If no entries exist yet, add an empty entry
                if not university_values or not any(university_values):
                    add_university_entry("")
                    
                # Add button to add new university entry
                add_btn = ttk.Button(frame, text="Add University", command=lambda: add_university_entry())
                add_btn.pack(anchor=tk.W, padx=5, pady=5)
                
                # Mark this path as the university list
                self.form_elements[path] = {"type": "university_list", "path": path}
            # Special handling for examinations list
            elif path.endswith("examinations") and isinstance(data, list):
                # We'll handle this as a complex list of examination objects
                examinations = data if data and data is not None else []
                
                # Container for examination entries
                exam_container = ttk.Frame(frame)
                exam_container.pack(fill=tk.X, padx=5, pady=5)
                
                # Keep track of examination entries
                self.examination_entries = []
                
                # Function to add examination entry
                def add_examination_entry(location="", count=0):
                    entry_frame = ttk.LabelFrame(exam_container, text="Examination")
                    entry_frame.pack(fill=tk.X, pady=2)
                    
                    # Location field
                    loc_frame = ttk.Frame(entry_frame)
                    loc_frame.pack(fill=tk.X, pady=2)
                    ttk.Label(loc_frame, text="Location:").pack(side=tk.LEFT, padx=5)
                    location_var = tk.StringVar(value=location)
                    location_entry = ttk.Entry(loc_frame, textvariable=location_var, width=30)
                    location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                    
                    # Count field
                    count_frame = ttk.Frame(entry_frame)
                    count_frame.pack(fill=tk.X, pady=2)
                    ttk.Label(count_frame, text="Count:").pack(side=tk.LEFT, padx=5)
                    count_var = tk.StringVar(value=str(count))
                    count_entry = ttk.Entry(count_frame, textvariable=count_var, width=10)
                    count_entry.pack(side=tk.LEFT, padx=5)
                    
                    # Remove button
                    remove_btn = ttk.Button(entry_frame, text="Remove Examination", 
                                          command=lambda: remove_examination(entry_frame, location_var, count_var))
                    remove_btn.pack(anchor=tk.W, padx=5, pady=5)
                    
                    exam_entry = {"frame": entry_frame, "location": location_var, "count": count_var}
                    self.examination_entries.append(exam_entry)
                    return exam_entry
                
                def remove_examination(frame, location_var, count_var):
                    # Find the examination entry to remove
                    for i, entry in enumerate(self.examination_entries):
                        if entry["location"] == location_var and entry["count"] == count_var:
                            self.examination_entries.pop(i)
                            break
                    frame.destroy()
                
                # Add existing examinations
                for exam in examinations:
                    if isinstance(exam, dict):
                        add_examination_entry(
                            location=exam.get("location", ""),
                            count=exam.get("count", 0)
                        )
                
                # If no examinations exist yet, add an empty one
                if not examinations:
                    add_examination_entry()
                    
                # Add button to add new examination
                add_btn = ttk.Button(frame, text="Add Examination", command=lambda: add_examination_entry())
                add_btn.pack(anchor=tk.W, padx=5, pady=5)
                
                # Mark this path as the examinations list
                self.form_elements[path] = {"type": "examinations_list", "path": path}
            else:
                # Generic list handling
                for i, item in enumerate(data):
                    item_frame = ttk.Frame(frame)
                    item_frame.pack(fill=tk.X, padx=5, pady=2)
                    
                    ttk.Label(item_frame, text=f"[{i}]").pack(side=tk.LEFT, padx=2)
                    self.create_form(item, f"{path}[{i}]", item_frame)
                    
        else:
            # Create input for leaf values
            frame = ttk.Frame(parent_frame)
            frame.pack(fill=tk.X, pady=2)
            
            display_key = path.split('.')[-1] if path else ""
            ttk.Label(frame, text=f"{display_key}:").pack(side=tk.LEFT, padx=5)
            
            # Different input types based on data type
            if data is None:
                var = tk.StringVar(value="")
                entry = ttk.Entry(frame, textvariable=var)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                # Save the variable and its path
                self.form_elements[path] = {"type": "string", "var": var, "path": path}
                
            elif isinstance(data, bool):
                var = tk.BooleanVar(value=data)
                check = ttk.Checkbutton(frame, variable=var)
                check.pack(side=tk.LEFT, padx=5)
                
                # Save the variable and its path
                self.form_elements[path] = {"type": "boolean", "var": var, "path": path}
                
            elif isinstance(data, (int, float)):
                var = tk.StringVar(value=str(data))
                entry = ttk.Entry(frame, textvariable=var)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                # Save the variable and its path
                value_type = "int" if isinstance(data, int) else "float"
                self.form_elements[path] = {"type": value_type, "var": var, "path": path}
                
            elif isinstance(data, str):
                # Check if it looks like a date
                if "T" in data and "-" in data and ":" in data:
                    # It's likely a datetime string
                    var = tk.StringVar(value=data)
                    entry = ttk.Entry(frame, textvariable=var)
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                    
                    # Add a button to update to current time
                    update_btn = ttk.Button(frame, text="Update to Now", 
                                           command=lambda v=var: v.set(datetime.datetime.now().isoformat()))
                    update_btn.pack(side=tk.LEFT, padx=5)
                    
                    # Save the variable and its path
                    self.form_elements[path] = {"type": "datetime", "var": var, "path": path}
                else:
                    # Regular string
                    var = tk.StringVar(value=data)
                    entry = ttk.Entry(frame, textvariable=var)
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                    
                    # Save the variable and its path
                    self.form_elements[path] = {"type": "string", "var": var, "path": path}
    
    def update_json_from_form(self):
        """Update the JSON data structure with values from the form elements."""
        if not self.json_data:
            return
            
        # Ensure the response_text exists
        if "response_text" not in self.json_data:
            self.json_data["response_text"] = {}
            
        # Special handling for author object
        for path, element_info in self.form_elements.items():
            if element_info.get("type") == "author_object":
                # Get author data from the form
                first_name = element_info["first_name"].get()
                last_name = element_info["last_name"].get()
                
                # Create author object
                author_data = {
                    "first_name": first_name,
                    "last_name": last_name
                }
                
                # Update author in the response_text
                self.json_data["response_text"]["author"] = author_data
                
        # Special handling for university list
        if hasattr(self, 'university_entries'):
            universities = [entry.get() for entry in self.university_entries if entry.get().strip()]
            
            # Ensure the path exists - but we'll need to do this differently based on the parent path
            # For now, we'll handle it for "personal_data.education.university"
            if "personal_data" not in self.json_data["response_text"]:
                self.json_data["response_text"]["personal_data"] = {}
            if "education" not in self.json_data["response_text"]["personal_data"]:
                self.json_data["response_text"]["personal_data"]["education"] = {}
                
            # Update universities
            self.json_data["response_text"]["personal_data"]["education"]["university"] = universities
        
        # Special handling for examinations list
        if hasattr(self, 'examination_entries'):
            examinations = []
            for exam_entry in self.examination_entries:
                location = exam_entry["location"].get()
                count_str = exam_entry["count"].get()
                
                try:
                    count = int(count_str)
                except ValueError:
                    count = 0
                    
                # Only add if we have a location (required field)
                if location.strip():
                    examinations.append({
                        "location": location,
                        "count": count
                    })
            
            # Ensure the path exists
            if "personal_data" not in self.json_data["response_text"]:
                self.json_data["response_text"]["personal_data"] = {}
                
            # Update examinations
            self.json_data["response_text"]["personal_data"]["examinations"] = examinations
        
        # Handle all other form elements based on their paths
        for path, element_info in self.form_elements.items():
            # Skip specially handled types
            if element_info.get("type") in ["author_object", "university_list", "examinations_list"]:
                continue
                
            # Get the variable and its value
            var = element_info.get("var")
            if not var:
                continue
                
            # Get the value based on variable type
            if isinstance(var, tk.BooleanVar):
                value = var.get()
            else:  # All other vars are StringVar
                value = var.get()
                
                # Convert to appropriate type if needed
                if element_info.get("type") == "int":
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                elif element_info.get("type") == "float":
                    try:
                        value = float(value)
                    except ValueError:
                        pass
            
            # Update the JSON structure using the path
            # Skip array indices in path
            if "[" in path and "]" in path:
                self.logger.debug(f"Skipping array item path: {path}")
                continue
                
            # Handle special case for response_text.X paths
            if path.startswith("response_text."):
                # Extract just the part after response_text.
                path_in_response = path[len("response_text."):]
                path_parts = path_in_response.split('.')
                
                # Navigate to the correct position in response_text
                current = self.json_data["response_text"]
                for i, part in enumerate(path_parts):
                    if i == len(path_parts) - 1:
                        # Last part - set the value
                        current[part] = value
                    else:
                        # Create nested dictionaries if they don't exist
                        if part not in current:
                            current[part] = {}
                        current = current[part]
            else:
                # Regular top-level keys like provider, model, etc.
                path_parts = path.split('.')
                current = self.json_data
                
                # Navigate to the right position in the JSON structure
                for i, part in enumerate(path_parts):
                    if i == len(path_parts) - 1:
                        # Last part - set the value
                        current[part] = value
                    else:
                        # Create nested dictionaries if they don't exist
                        if part not in current:
                            current[part] = {}
                        current = current[part]
        
        # Debug info
        self.logger.debug("Updated JSON data: %s", self.json_data)
    
    def next_image(self):
        """Navigate to the next image in the folder."""
        self.logger.info(f"Next image button clicked. Current state: index={self.current_image_index}, images count={len(self.images_in_folder)}")
        
        if not self.images_in_folder:
            self.logger.warning("No images in folder, can't navigate")
            messagebox.showinfo("Navigation", "No images available in the current folder.")
            return
            
        if self.current_image_index == -1:
            self.logger.warning("Current image index is -1, refreshing image list")
            self.update_images_in_folder()
            if self.current_image_index == -1:
                messagebox.showinfo("Navigation", "Can't determine current image position in folder.")
                return
            
        # Check if there are unsaved changes
        if self.check_for_save():
            # Save current image's JSON if needed
            self.save_json(show_message=False)
            
        # Go to next image
        try:
            next_index = (self.current_image_index + 1) % len(self.images_in_folder)
            self.logger.info(f"Moving to next image at index {next_index}")
            next_image_path = self.images_in_folder[next_index]
            self.logger.info(f"Next image path: {next_image_path}")
            self.load_image(next_image_path)
        except Exception as e:
            self.logger.error(f"Error navigating to next image: {str(e)}", exc_info=True)
            messagebox.showerror("Navigation Error", f"Failed to load next image: {str(e)}")
    
    def previous_image(self):
        """Navigate to the previous image in the folder."""
        self.logger.info(f"Previous image button clicked. Current state: index={self.current_image_index}, images count={len(self.images_in_folder)}")
        
        if not self.images_in_folder:
            self.logger.warning("No images in folder, can't navigate")
            messagebox.showinfo("Navigation", "No images available in the current folder.")
            return
            
        if self.current_image_index == -1:
            self.logger.warning("Current image index is -1, refreshing image list")
            self.update_images_in_folder()
            if self.current_image_index == -1:
                messagebox.showinfo("Navigation", "Can't determine current image position in folder.")
                return
            
        # Check if there are unsaved changes
        if self.check_for_save():
            # Save current image's JSON if needed
            self.save_json(show_message=False)
            
        # Go to previous image
        try:
            prev_index = (self.current_image_index - 1) % len(self.images_in_folder)
            self.logger.info(f"Moving to previous image at index {prev_index}")
            prev_image_path = self.images_in_folder[prev_index]
            self.logger.info(f"Previous image path: {prev_image_path}")
            self.load_image(prev_image_path)
        except Exception as e:
            self.logger.error(f"Error navigating to previous image: {str(e)}", exc_info=True)
            messagebox.showerror("Navigation Error", f"Failed to load previous image: {str(e)}")
    
    def check_for_save(self):
        """Check if the current JSON has changes that should be saved."""
        if not self.current_json_path or not self.json_data:
            return False
            
        # For now, always return True to auto-save on navigation
        # In the future, we could implement change detection
        return True
    
    def save_json(self, show_message=True):
        """Save the JSON data to file."""
        if not self.current_json_path or not self.json_data:
            if show_message:
                messagebox.showwarning("Warning", "No JSON file loaded to save.")
            return
            
        try:
            # Update JSON data from form
            print("Before update:", self.json_data)
            self.update_json_from_form()
            print("After update:", self.json_data)
            
            # Check if authors were properly updated
            if "response_text" in self.json_data and "metadata" in self.json_data["response_text"]:
                print("Author value:", self.json_data["response_text"]["metadata"].get("author"))
            
            # Save to file
            with open(self.current_json_path, 'w') as f:
                json.dump(self.json_data, f, indent=4)
                
            if show_message:
                messagebox.showinfo("Success", f"JSON saved to {self.current_json_path}")
            
        except Exception as e:
            print(f"Error saving: {str(e)}")
            import traceback
            traceback.print_exc()
            if show_message:
                messagebox.showerror("Error", f"Failed to save JSON: {str(e)}")

def main():
    # Set up logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('groundtruther.log')
        ]
    )
    
    root = tk.Tk()
    
    # Set up keyboard shortcuts
    app = MetadataEditor(root)
    
    # Add keyboard shortcuts
    root.bind('<Right>', lambda event: app.next_image())
    root.bind('<Left>', lambda event: app.previous_image())
    root.bind('<Control-s>', lambda event: app.save_json())
    
    root.mainloop()

if __name__ == "__main__":
    main()