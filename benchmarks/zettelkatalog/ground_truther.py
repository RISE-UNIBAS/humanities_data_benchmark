import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import os
import argparse
import logging
from typing import Dict, Any, List, Optional, Union
import datetime
from dataclass import Author, Publication, Examination, LibraryReference, Document, WorkType

class Config:
    def __init__(self, image_dir=None, json_dir=None, output_dir=None, prefix="request_T66_"):
        self.image_dir = image_dir
        self.json_dir = json_dir
        self.output_dir = output_dir
        self.prefix = prefix
        self.config_file = os.path.join(os.path.expanduser("~"), ".groundtruther_config.json")
        
    def save_config(self):
        """Save configuration to a JSON file."""
        config_data = {
            "image_dir": self.image_dir,
            "json_dir": self.json_dir,
            "output_dir": self.output_dir,
            "prefix": self.prefix
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"Error saving config: {str(e)}")

            return False
    
    def load_config(self):
        """Load configuration from JSON file."""
        if not os.path.exists(self.config_file):
            return False
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            # Only update values that are not explicitly set
            if self.image_dir is None and "image_dir" in config_data:
                self.image_dir = config_data["image_dir"]
                
            if self.json_dir is None and "json_dir" in config_data:
                self.json_dir = config_data["json_dir"]
                
            if self.output_dir is None and "output_dir" in config_data:
                self.output_dir = config_data["output_dir"]
                
            if self.prefix == "request_T66_" and "prefix" in config_data:
                self.prefix = config_data["prefix"]
                
            return True
        except Exception as e:
            logging.error(f"Error loading config: {str(e)}")
            return False

class MetadataEditor:
    def __init__(self, root, config: Config):
        self.root = root
        self.root.title("Ground Truther")
        self.root.geometry("1200x800")
        
        # Set up logger
        import logging
        self.logger = logging.getLogger(__name__)
        
        self.config = config
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
        
        # Configuration panel
        config_frame = ttk.LabelFrame(right_frame, text="Configuration")
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Image directory
        img_dir_frame = ttk.Frame(config_frame)
        img_dir_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(img_dir_frame, text="Image Directory:").pack(side=tk.LEFT, padx=5)
        self.image_dir_var = tk.StringVar(value=self.config.image_dir or "")
        img_dir_entry = ttk.Entry(img_dir_frame, textvariable=self.image_dir_var, width=30)
        img_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        def browse_img_dir():
            initial_dir = self.config.image_dir if self.config.image_dir else os.getcwd()
            dir_path = filedialog.askdirectory(title="Select Image Directory", initialdir=initial_dir)
            if dir_path:
                self.image_dir_var.set(dir_path)
                self.config.image_dir = dir_path
                # Auto-save config when directory is changed
                self.config.save_config()
                self.update_images_in_folder()
        
        ttk.Button(img_dir_frame, text="Browse...", command=browse_img_dir).pack(side=tk.LEFT, padx=5)
        
        # JSON directory
        json_dir_frame = ttk.Frame(config_frame)
        json_dir_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(json_dir_frame, text="JSON Directory:").pack(side=tk.LEFT, padx=5)
        self.json_dir_var = tk.StringVar(value=self.config.json_dir or "")
        json_dir_entry = ttk.Entry(json_dir_frame, textvariable=self.json_dir_var, width=30)
        json_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        def browse_json_dir():
            initial_dir = self.config.json_dir if self.config.json_dir else os.getcwd()
            dir_path = filedialog.askdirectory(title="Select JSON Directory", initialdir=initial_dir)
            if dir_path:
                self.json_dir_var.set(dir_path)
                self.config.json_dir = dir_path
                # Auto-save config when directory is changed
                self.config.save_config()
        
        ttk.Button(json_dir_frame, text="Browse...", command=browse_json_dir).pack(side=tk.LEFT, padx=5)
        
        # Output directory
        output_dir_frame = ttk.Frame(config_frame)
        output_dir_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(output_dir_frame, text="Output Directory:").pack(side=tk.LEFT, padx=5)
        self.output_dir_var = tk.StringVar(value=self.config.output_dir or "")
        output_dir_entry = ttk.Entry(output_dir_frame, textvariable=self.output_dir_var, width=30)
        output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        def browse_output_dir():
            initial_dir = self.config.output_dir if self.config.output_dir else os.getcwd()
            dir_path = filedialog.askdirectory(title="Select Output Directory", initialdir=initial_dir)
            if dir_path:
                self.output_dir_var.set(dir_path)
                self.config.output_dir = dir_path
                # Auto-save config when directory is changed
                self.config.save_config()
        
        ttk.Button(output_dir_frame, text="Browse...", command=browse_output_dir).pack(side=tk.LEFT, padx=5)
        
        # Prefix
        prefix_frame = ttk.Frame(config_frame)
        prefix_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(prefix_frame, text="JSON Prefix:").pack(side=tk.LEFT, padx=5)
        self.prefix_var = tk.StringVar(value=self.config.prefix)
        prefix_entry = ttk.Entry(prefix_frame, textvariable=self.prefix_var, width=20)
        prefix_entry.pack(side=tk.LEFT, padx=5)
        
        def update_prefix():
            self.config.prefix = self.prefix_var.get()
            # Auto-save config when prefix is changed
            self.config.save_config()
            messagebox.showinfo("Prefix Updated", f"JSON prefix updated to: {self.config.prefix}")
        
        ttk.Button(prefix_frame, text="Update", command=update_prefix).pack(side=tk.LEFT, padx=5)
        
        # Apply Changes
        def apply_config():
            self.config.image_dir = self.image_dir_var.get() if self.image_dir_var.get() else None
            self.config.json_dir = self.json_dir_var.get() if self.json_dir_var.get() else None
            self.config.output_dir = self.output_dir_var.get() if self.output_dir_var.get() else None
            self.config.prefix = self.prefix_var.get()
            
            # Log updated config
            self.logger.info(f"Updated configuration:")
            self.logger.info(f"  Image directory: {self.config.image_dir}")
            self.logger.info(f"  JSON directory: {self.config.json_dir}")
            self.logger.info(f"  Output directory: {self.config.output_dir}")
            self.logger.info(f"  JSON prefix: {self.config.prefix}")
            
            # Save configuration to file
            if self.config.save_config():
                self.logger.info("Configuration saved to file")
            else:
                self.logger.warning("Failed to save configuration to file")
            
            # Update the UI
            self.update_images_in_folder()
            messagebox.showinfo("Configuration", "Settings updated and saved successfully!")
        
        ttk.Button(config_frame, text="Apply Settings", command=apply_config).pack(anchor=tk.E, padx=5, pady=5)
        
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
        # Set initial directory based on configuration
        initial_dir = self.config.image_dir if self.config.image_dir else os.getcwd()
        
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")],
            initialdir=initial_dir
        )
        
        if file_path:
            self.load_image(file_path)
            
    def update_images_in_folder(self):
        """Find all image files in the configured image directory or current image folder."""
        # Determine which folder to scan
        folder = None
        
        # First priority: use the configured image directory
        if self.config.image_dir and os.path.isdir(self.config.image_dir):
            folder = self.config.image_dir
        # Second priority: use the directory of the current image
        elif self.current_image_path and os.path.exists(self.current_image_path):
            folder = os.path.dirname(self.current_image_path)
            
        if not folder:
            self.logger.info("No valid image directory found, cannot update folder listing")
            self.images_in_folder = []
            self.current_image_index = -1
            self.update_counter_label()
            return
            
        self.images_in_folder = []
        
        self.logger.info(f"Scanning folder for images: {folder}")
        
        # Get all image files in the folder
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        try:
            for file in os.listdir(folder):
                if file.lower().endswith(image_extensions):
                    full_path = os.path.join(folder, file)
                    self.images_in_folder.append(full_path)
            
            # Sort alphabetically
            self.images_in_folder.sort()
            
            self.logger.info(f"Found {len(self.images_in_folder)} images in folder")
        except Exception as e:
            self.logger.error(f"Error scanning folder {folder}: {str(e)}", exc_info=True)
            self.images_in_folder = []
        
        # Find current image index
        if self.current_image_path and self.images_in_folder:
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
        else:
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
        image_basename = os.path.basename(os.path.splitext(file_path)[0])
        
        # Create a list of places to look for the JSON file
        json_search_paths = []
        
        # IMPORTANT: The order of these paths determines the priority for loading JSONs!
        
        # First priority: check for *any* JSON file in the JSON directory that might match
        if self.config.json_dir and os.path.isdir(self.config.json_dir):
            # Look for any JSON file that could match this image (without assuming prefix)
            try:
                for json_filename in os.listdir(self.config.json_dir):
                    if json_filename.lower().endswith('.json'):
                        # Extract image name part from JSON filename
                        json_base = os.path.splitext(json_filename)[0]
                        # Check if this JSON might be for our image by checking if image_basename is in it
                        if image_basename in json_base:
                            # Found a potential match
                            json_path = os.path.join(self.config.json_dir, json_filename)
                            json_search_paths.append(json_path)
                            self.logger.info(f"Adding potential JSON match: {json_path}")
            except Exception as e:
                self.logger.error(f"Error scanning JSON directory: {str(e)}")
        
        # Second priority: check for *any* JSON file in the output directory that might match
        if self.config.output_dir and os.path.isdir(self.config.output_dir):
            try:
                for json_filename in os.listdir(self.config.output_dir):
                    if json_filename.lower().endswith('.json'):
                        json_base = os.path.splitext(json_filename)[0]
                        if image_basename in json_base:
                            json_path = os.path.join(self.config.output_dir, json_filename)
                            if json_path not in json_search_paths:  # Avoid duplicates
                                json_search_paths.append(json_path)
                                self.logger.info(f"Adding potential JSON match from output dir: {json_path}")
            except Exception as e:
                self.logger.error(f"Error scanning output directory: {str(e)}")
        
        # Third priority: Check image directory
        # Only use this if no JSON directory is specified or if we want to always check image dir
        if not self.config.json_dir or not os.path.isdir(self.config.json_dir):
            try:
                image_dir = os.path.dirname(file_path)
                for json_filename in os.listdir(image_dir):
                    if json_filename.lower().endswith('.json'):
                        json_base = os.path.splitext(json_filename)[0]
                        if image_basename in json_base:
                            json_path = os.path.join(image_dir, json_filename)
                            if json_path not in json_search_paths:  # Avoid duplicates
                                json_search_paths.append(json_path)
                                self.logger.info(f"Adding potential JSON match from image dir: {json_path}")
            except Exception as e:
                self.logger.error(f"Error scanning image directory: {str(e)}")
        
        # Try each possible JSON path
        found_json = False
        for possible_json_path in json_search_paths:
            self.logger.info(f"Checking for JSON file: {possible_json_path}")
            if os.path.exists(possible_json_path):
                self.logger.info(f"Found JSON file: {possible_json_path}")
                self.current_json_path = possible_json_path
                self.json_label.config(text=f"JSON: {os.path.basename(possible_json_path)}")
                self.load_json()
                found_json = True
                break
        
        if not found_json:
            # Clear the form if no JSON found
            self.logger.warning(f"No JSON file found for this image")
            
            # If JSON dir is specified, create a new path there
            if self.config.json_dir and os.path.isdir(self.config.json_dir):
                new_json_path = os.path.join(self.config.json_dir, json_filename)
                self.logger.info(f"No JSON found, will create at: {new_json_path} when saved")
                self.current_json_path = new_json_path
                self.json_label.config(text=f"JSON: {os.path.basename(new_json_path)} (new)")
            # Otherwise use output dir if specified
            elif self.config.output_dir and os.path.isdir(self.config.output_dir):
                new_json_path = os.path.join(self.config.output_dir, json_filename)
                self.logger.info(f"No JSON found, will create at: {new_json_path} when saved")
                self.current_json_path = new_json_path
                self.json_label.config(text=f"JSON: {os.path.basename(new_json_path)} (new)")
            # Last resort: create in the same directory as the image
            else:
                new_json_path = os.path.join(os.path.dirname(file_path), json_filename)
                self.logger.info(f"No JSON found, will create at: {new_json_path} when saved")
                self.current_json_path = new_json_path
                self.json_label.config(text=f"JSON: {os.path.basename(new_json_path)} (new)")
            
            # Create empty JSON data structure
            self.json_data = {
                "provider": "",
                "model": "",
                "test_time": 0,
                "execution_time": datetime.datetime.now().isoformat(),
                "response_text": {
                    "type": {
                        "type": ""  # Literal["Dissertation or thesis", "Other"]
                    },
                    "author": {
                        "last_name": "",
                        "first_name": ""
                    },
                    "publication": {
                        "title": "",
                        "year": 0,
                        "place": "",
                        "pages": "",
                        "publisher": "",
                        "format": "",
                        "reprint_note": ""
                    },
                    "examination": {
                        "place": "",
                        "year": 0
                    },
                    "library_reference": {
                        "shelfmark": "",
                        "publication_number": "",
                        "subjects": ""
                    }
                },
                "scores": {}
            }
            
            # Clear existing form elements
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            self.form_elements = {}
            
            # Create form based on empty JSON structure
            self.create_form(self.json_data, "", self.scrollable_frame)
    
    def open_json(self):
        # Set initial directory based on configuration
        initial_dir = self.config.json_dir if self.config.json_dir and os.path.isdir(self.config.json_dir) else os.getcwd()
        
        file_path = filedialog.askopenfilename(
            title="Select JSON",
            filetypes=[("JSON files", "*.json")],
            initialdir=initial_dir
        )
        
        if file_path:
            # Check if the file is from the configured JSON directory
            # If we have a JSON directory set but selected a file from elsewhere, copy it to the JSON directory
            if self.config.json_dir and os.path.isdir(self.config.json_dir):
                file_dir = os.path.dirname(file_path)
                if os.path.normpath(file_dir) != os.path.normpath(self.config.json_dir):
                    # File is from a different directory
                    self.logger.info(f"Selected JSON is not from configured JSON directory")
                    
                    # Ask if user wants to copy to JSON directory
                    result = messagebox.askyesno("JSON Location", 
                                             f"The selected JSON file is not from your configured JSON directory.\n\n"
                                             f"Would you like to copy it to the JSON directory?\n"
                                             f"({self.config.json_dir})")
                    
                    if result:
                        # Copy the file to the JSON directory
                        import shutil
                        dest_path = os.path.join(self.config.json_dir, os.path.basename(file_path))
                        self.logger.info(f"Copying {file_path} to {dest_path}")
                        
                        try:
                            shutil.copy2(file_path, dest_path)
                            file_path = dest_path  # Use the copied file
                            self.logger.info(f"Successfully copied to JSON directory")
                            messagebox.showinfo("File Copied", f"The file has been copied to the JSON directory.")
                        except Exception as e:
                            self.logger.error(f"Failed to copy file: {str(e)}")
                            messagebox.showerror("Error", f"Failed to copy file: {str(e)}")
            
            self.current_json_path = file_path
            self.json_label.config(text=f"JSON: {os.path.basename(file_path)}")
            self.load_json()
            
            # Try to find matching image file based on the JSON filename
            json_basename = os.path.basename(file_path)
            # Remove .json extension
            json_base = os.path.splitext(json_basename)[0]
            
            # Extract potential image name from the JSON filename by trying different methods
            potential_image_names = []
            
            # Method 1: Try removing specific prefixes we know about
            prefixes_to_try = [self.config.prefix, "request_", "response_", "data_"]
            for prefix in prefixes_to_try:
                if json_base.startswith(prefix):
                    image_name = json_base[len(prefix):]
                    if image_name:  # Only add if not empty
                        potential_image_names.append(image_name)
                        self.logger.info(f"Potential image name after removing '{prefix}': {image_name}")
            
            # Method 2: Try using the entire basename as a fallback
            potential_image_names.append(json_base)
            
            # Define possible image extensions
            possible_image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
            
            # Create a list of directories to search for the image
            image_search_dirs = []
            
            # First priority: configured image directory
            if self.config.image_dir and os.path.isdir(self.config.image_dir):
                image_search_dirs.append(self.config.image_dir)
                self.logger.info(f"Adding image search path (specified image dir): {self.config.image_dir}")
            
            # Only check JSON directory if no image directory is specified
            if not self.config.image_dir or not os.path.isdir(self.config.image_dir):
                # Second priority: same directory as the JSON file
                image_search_dirs.append(os.path.dirname(file_path))
                self.logger.info(f"Adding image search path (JSON dir): {os.path.dirname(file_path)}")
            
            # Search for matching image in all directories
            found_image = False
            
            # First pass: try exact matches for our potential image names
            for search_dir in image_search_dirs:
                if found_image:
                    break
                    
                for image_name in potential_image_names:
                    if found_image:
                        break
                        
                    for ext in possible_image_extensions:
                        possible_image_path = os.path.join(search_dir, image_name + ext)
                        self.logger.info(f"Looking for exact match image file: {possible_image_path}")
                        
                        if os.path.exists(possible_image_path):
                            self.logger.info(f"Found image file: {possible_image_path}")
                            self.current_image_path = possible_image_path
                            self.image_label.config(text=f"Image: {os.path.basename(possible_image_path)}")
                            self.display_image()
                            
                            # Find all images in the folder for navigation
                            self.update_images_in_folder()
                            found_image = True
                            break
            
            # Second pass: if no exact match found, try listing all images and check for partial matches
            if not found_image:
                for search_dir in image_search_dirs:
                    if found_image:
                        break
                    
                    # List all image files in the directory
                    try:
                        for filename in os.listdir(search_dir):
                            file_base, file_ext = os.path.splitext(filename)
                            if file_ext.lower() in possible_image_extensions:
                                # Check if any of our potential image names is contained within this image filename
                                for image_name in potential_image_names:
                                    if image_name in file_base or file_base in image_name:
                                        # Found a potential match
                                        possible_image_path = os.path.join(search_dir, filename)
                                        self.logger.info(f"Found partial match image file: {possible_image_path}")
                                        
                                        # Ask user to confirm this match if it's not an exact match
                                        result = messagebox.askyesno("Confirm Image Match",
                                                                  f"Is this the correct image for the JSON?\n\n"
                                                                  f"JSON: {json_basename}\n"
                                                                  f"Image: {filename}")
                                        
                                        if result:
                                            self.current_image_path = possible_image_path
                                            self.image_label.config(text=f"Image: {filename}")
                                            self.display_image()
                                            
                                            # Find all images in the folder for navigation
                                            self.update_images_in_folder()
                                            found_image = True
                                            break
                                
                                if found_image:
                                    break
                    except Exception as e:
                        self.logger.error(f"Error scanning directory for images: {str(e)}")
                        continue
    
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
            # Try to load the JSON file with standard json.load
            try:
                with open(self.current_json_path, 'r', encoding='utf-8') as f:
                    self.json_data = json.load(f)
            except json.JSONDecodeError as decode_error:
                # If there's a decoding error, try to clean the file and reload it
                self.logger.warning(f"JSON decode error: {str(decode_error)}. Attempting to clean file.")
                
                # Read the file as text
                with open(self.current_json_path, 'r', encoding='utf-8', errors='replace') as f:
                    json_text = f.read()
                
                # Remove control characters
                json_text = self.clean_json_string(json_text)
                
                # Try to parse the cleaned text
                try:
                    self.json_data = json.loads(json_text)
                    self.logger.info("Successfully loaded JSON after cleaning")
                    
                    # Note: we don't modify the original JSON file, we'll only save
                    # to the output directory when the user chooses to save
                    
                    messagebox.showinfo("JSON Cleaned", 
                                      f"The JSON file contained invalid characters and has been cleaned.\n\n"
                                      f"The cleaned data will be used but the original file is unchanged.\n"
                                      f"Use Save JSON to save the cleaned version.")
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse JSON even after cleaning: {str(e)}")
                    
                    # FINAL ATTEMPT: Try to repair the structure more aggressively
                    try:
                        self.logger.warning("Attempting aggressive JSON repair...")
                        repaired_json = self.repair_json_structure(json_text)
                        self.json_data = repaired_json
                        
                        messagebox.showinfo("JSON Repaired", 
                                         f"The JSON file was severely corrupted but has been repaired.\n\n"
                                         f"The repaired data will be used but the original file is unchanged.\n"
                                         f"Use Save JSON to save the repaired version.\n\n"
                                         f"Some data may have been lost in the repair process.")
                        
                    except Exception as repair_error:
                        self.logger.error(f"Failed to repair JSON: {str(repair_error)}")
                        raise e  # Re-raise the original JSON decode error
            
            # Ensure expected structure exists
            if "response_text" not in self.json_data:
                self.json_data["response_text"] = {}
                
            # Initialize type structure if needed
            if "type" not in self.json_data["response_text"]:
                self.json_data["response_text"]["type"] = {
                    "type": ""  # Literal["Dissertation or thesis", "Other"]
                }
                
            # Initialize author structure if needed
            if "author" not in self.json_data["response_text"]:
                self.json_data["response_text"]["author"] = {
                    "first_name": "",
                    "last_name": ""
                }
            
            # Initialize publication structure if needed
            if "publication" not in self.json_data["response_text"]:
                self.json_data["response_text"]["publication"] = {
                    "title": "",
                    "year": 0,
                    "place": None,
                    "pages": None,
                    "publisher": None,
                    "format": None,
                    "reprint_note": None
                }
                
            # Initialize examination structure if needed
            if "examination" not in self.json_data["response_text"]:
                self.json_data["response_text"]["examination"] = None
            
            # Initialize library_reference structure if needed
            if "library_reference" not in self.json_data["response_text"]:
                self.json_data["response_text"]["library_reference"] = None
                
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
            
            # Improved error message with recovery options
            result = messagebox.askquestion("Error Loading JSON", 
                               f"Failed to load JSON: {str(e)}\n\n"
                               f"Would you like to create a new empty JSON file instead?",
                               icon='error')
                               
            if result == 'yes':
                # Create a new empty JSON structure
                self.json_data = {
                    "provider": "",
                    "model": "",
                    "test_time": 0,
                    "execution_time": datetime.datetime.now().isoformat(),
                    "response_text": {
                        "type": {
                            "type": ""  # Literal["Dissertation or thesis", "Other"]
                        },

                        "author": {
                            "last_name": "",
                            "first_name": ""
                        },
                        "publication": {
                            "title": "",
                            "year": 0,
                            "place": "",
                            "pages": "",
                            "publisher": "",
                            "format": "",
                            "reprint_note": ""
                        },
                        "examination": {
                            "place": "",
                            "year": 0
                        },
                        "library_reference": {
                            "shelfmark": "",
                            "publication_number": "",
                            "subjects": ""
                        }
                    },
                    "scores": {}
                }
                
                # Create empty form
                for widget in self.scrollable_frame.winfo_children():
                    widget.destroy()
                    
                self.form_elements = {}
                self.create_form(self.json_data, "", self.scrollable_frame)
                
                messagebox.showinfo("New JSON Created", 
                                  "A new empty JSON structure has been created.\n\n"
                                  "You can now fill in the data and save it.")
    
    def repair_json_structure(self, json_text):
        """Last resort attempt to repair severely corrupted JSON by recreating a minimal valid structure."""
        self.logger.info("Attempting to extract any valid data from corrupted JSON")
        
        # Start with a minimal valid structure
        repaired_data = {
            "provider": "",
            "model": "",
            "test_time": 0,
            "execution_time": datetime.datetime.now().isoformat(),
            "response_text": {
                "type": {
                    "type": ""  # Literal["Dissertation or thesis", "Other"]
                },
                "author": {
                    "last_name": "",
                    "first_name": ""
                },
                "publication": {
                    "title": "",
                    "year": 0,
                    "place": "",
                    "pages": "",
                    "publisher": "",
                    "format": "",
                    "reprint_note": ""
                },
                "examination": {
                    "place": "",
                    "year": 0
                },
                "library_reference": {
                    "shelfmark": "",
                    "publication_number": "",
                    "subjects": ""
                }
            },
            "scores": {}
        }
        
        # Try to extract values using regex patterns
        import re
        
        # Look for author name
        author_match = re.search(r'"author".*?"last_name".*?:"(.*?)".*?"first_name".*?:"(.*?)"', json_text, re.DOTALL)
        if author_match:
            repaired_data["response_text"]["author"]["last_name"] = author_match.group(1).strip()
            repaired_data["response_text"]["author"]["first_name"] = author_match.group(2).strip()
            
        # Look for publication title and year
        title_match = re.search(r'"title".*?:"(.*?)"', json_text, re.DOTALL)
        if title_match:
            repaired_data["response_text"]["publication"]["title"] = title_match.group(1).strip()
            
        # Look for publication place and year
        place_match = re.search(r'"place".*?:"(.*?)"', json_text, re.DOTALL)
        if place_match:
            repaired_data["response_text"]["publication"]["place"] = place_match.group(1).strip()
            
        year_match = re.search(r'"year".*?:(\d+)', json_text)
        if year_match:
            try:
                repaired_data["response_text"]["publication"]["year"] = int(year_match.group(1))
            except:
                pass
                
        # Look for document type
        type_match = re.search(r'"type".*?:"(.*?)"', json_text, re.DOTALL)
        if type_match:
            repaired_data["response_text"]["type"]["type"] = type_match.group(1).strip()
            
        # Look for library reference
        shelfmark_match = re.search(r'"shelfmark".*?:"(.*?)"', json_text, re.DOTALL)
        if shelfmark_match:
            repaired_data["response_text"]["library_reference"]["shelfmark"] = shelfmark_match.group(1).strip()
        
        publication_number_match = re.search(r'"publication_number".*?:"(.*?)"', json_text, re.DOTALL)
        if publication_number_match:
            repaired_data["response_text"]["library_reference"]["publication_number"] = publication_number_match.group(1).strip()
            
        subjects_match = re.search(r'"subjects".*?:"(.*?)"', json_text, re.DOTALL)
        if subjects_match:
            repaired_data["response_text"]["library_reference"]["subjects"] = subjects_match.group(1).strip()
            
        # Look for examination details
        examination_place_match = re.search(r'"examination".*?"place".*?:"(.*?)"', json_text, re.DOTALL)
        if examination_place_match:
            repaired_data["response_text"]["examination"]["place"] = examination_place_match.group(1).strip()
            
        examination_year_match = re.search(r'"examination".*?"year".*?:(\d+)', json_text, re.DOTALL)
        if examination_year_match:
            try:
                repaired_data["response_text"]["examination"]["year"] = int(examination_year_match.group(1))
            except:
                pass
            
        # Log what we managed to extract
        self.logger.info(f"Extracted data from corrupted JSON: {repaired_data}")
        
        return repaired_data
            
    def clean_json_string(self, json_str):
        """Remove invalid control characters from JSON string using a more robust approach."""
        import re
        
        # 1. First approach: Regular expression to remove all control characters except allowed ones
        # This removes all ASCII control characters (0-31) except newline, tab, and carriage return
        cleaned_str = re.sub(r'[\x00-\x09\x0B\x0C\x0E-\x1F\x7F]', '', json_str)
        
        # 2. Second approach: Character by character examination and removal
        result = []
        for char in cleaned_str:
            # Only keep characters that are valid in JSON
            if ord(char) >= 32 or char in ['\n', '\r', '\t']:
                result.append(char)
                
        cleaned_str = ''.join(result)
        
        # 3. Additional escaping for common problem characters in strings
        # Look for unescaped quotes and control chars in strings
        try:
            # Find string parts of the JSON (text between quotes)
            string_pattern = r'"([^"\\]|\\.|)*?"'
            matches = re.finditer(string_pattern, cleaned_str)
            
            # For each string, clean it separately
            for match in matches:
                string_value = match.group(0)
                # Escape any remaining control characters
                fixed_string = re.sub(r'[\x00-\x1F\x7F]', lambda m: f'\\u{ord(m.group(0)):04x}', string_value)
                # Replace in the original string
                cleaned_str = cleaned_str.replace(string_value, fixed_string)
        except:
            # If regex matching fails, continue with what we have so far
            pass
            
        # Log the cleaning result
        self.logger.info(f"Cleaned JSON string, removed {len(json_str) - len(cleaned_str)} characters")
        
        return cleaned_str
    
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
            
            # Special handling for type (WorkType)
            if path.endswith("type") and not any(s in path for s in ["[", "]"]) and isinstance(data, dict) and "type" in data:
                # This is the WorkType object in response_text.type
                # Create a frame for the type field
                type_frame = ttk.Frame(frame)
                type_frame.pack(fill=tk.X, padx=5, pady=5)
                
                # Create field for type
                type_field_frame = ttk.Frame(type_frame)
                type_field_frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(type_field_frame, text="Type:").pack(side=tk.LEFT, padx=5)
                type_var = tk.StringVar(value=data.get("type", "") if isinstance(data, dict) else "")
                
                # Create a dropdown for type with allowed values
                type_combo = ttk.Combobox(type_field_frame, textvariable=type_var, width=40)
                type_combo['values'] = ("Dissertation or thesis", "Other")
                type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                # Save the variable
                self.form_elements[f"{path}.type"] = {"type": "string", "var": type_var, "path": f"{path}.type"}
                
                # Special handling for WorkType object
                self.form_elements[path] = {"type": "work_type_object", "path": path, "type": type_var}
            
            # Special handling for author
            elif path.endswith("author") and not any(s in path for s in ["[", "]"]):
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
            # Special handling for examination (singular, not a list in the new structure)
            elif path.endswith("examination") and isinstance(data, dict):
                # We'll handle this as a single examination object
                # Container for examination entry
                exam_container = ttk.Frame(frame)
                exam_container.pack(fill=tk.X, padx=5, pady=5)
                
                # Keep track of examination entries
                self.examination_entries = []
                
                # Function to create examination entry
                def create_examination_entry(place="", year=0):
                    entry_frame = ttk.LabelFrame(exam_container, text="Examination")
                    entry_frame.pack(fill=tk.X, pady=2)
                    
                    # Place field
                    place_frame = ttk.Frame(entry_frame)
                    place_frame.pack(fill=tk.X, pady=2)
                    ttk.Label(place_frame, text="Place:").pack(side=tk.LEFT, padx=5)
                    place_var = tk.StringVar(value=place)
                    place_entry = ttk.Entry(place_frame, textvariable=place_var, width=30)
                    place_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                    
                    # Year field
                    year_frame = ttk.Frame(entry_frame)
                    year_frame.pack(fill=tk.X, pady=2)
                    ttk.Label(year_frame, text="Year:").pack(side=tk.LEFT, padx=5)
                    year_var = tk.StringVar(value=str(year))
                    year_entry = ttk.Entry(year_frame, textvariable=year_var, width=10)
                    year_entry.pack(side=tk.LEFT, padx=5)
                    
                    exam_entry = {"frame": entry_frame, "location": place_var, "count": year_var}
                    self.examination_entries.append(exam_entry)
                    return exam_entry
                
                # Create the examination entry with existing data
                place = data.get("place", "")
                year = data.get("year", 0)
                create_examination_entry(place=place, year=year)
                
                # Mark this path as the examination object
                self.form_elements[path] = {"type": "examination_object", "path": path}
                
            # Special handling for library_reference
            elif path.endswith("library_reference") and isinstance(data, dict):
                # We'll handle this as a single library_reference object
                # Container for library_reference entry
                ref_container = ttk.Frame(frame)
                ref_container.pack(fill=tk.X, padx=5, pady=5)
                
                # Keep track of library_reference entries
                self.library_reference_entry = {}
                
                # Create the form elements
                entry_frame = ttk.LabelFrame(ref_container, text="Library Reference")
                entry_frame.pack(fill=tk.X, pady=2)
                
                # Shelfmark field
                shelfmark_frame = ttk.Frame(entry_frame)
                shelfmark_frame.pack(fill=tk.X, pady=2)
                ttk.Label(shelfmark_frame, text="Shelfmark:").pack(side=tk.LEFT, padx=5)
                shelfmark_var = tk.StringVar(value=data.get("shelfmark", ""))
                shelfmark_entry = ttk.Entry(shelfmark_frame, textvariable=shelfmark_var, width=30)
                shelfmark_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                # publication_number field
                publication_number_frame = ttk.Frame(entry_frame)
                publication_number_frame.pack(fill=tk.X, pady=2)
                ttk.Label(publication_number_frame, text="publication_number:").pack(side=tk.LEFT, padx=5)
                publication_number_var = tk.StringVar(value=data.get("publication_number", ""))
                publication_number_entry = ttk.Entry(publication_number_frame, textvariable=publication_number_var, width=30)
                publication_number_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                # subjects field
                subjects_frame = ttk.Frame(entry_frame)
                subjects_frame.pack(fill=tk.X, pady=2)
                ttk.Label(subjects_frame, text="Subjects:").pack(side=tk.LEFT, padx=5)
                subjects_var = tk.StringVar(value=data.get("subjects", ""))
                subjects_entry = ttk.Entry(subjects_frame, textvariable=subjects_var, width=30)
                subjects_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                # Save the references
                self.library_reference_entry = {
                    "frame": entry_frame,
                    "shelfmark": shelfmark_var,
                    "publication_number": publication_number_var,
                    "subjects": subjects_var
                }
                
                # Mark this path as the library_reference object
                self.form_elements[path] = {"type": "library_reference_object", "path": path}
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
            
        # Special handling for work type object
        for path, element_info in self.form_elements.items():
            if element_info.get("type") == "work_type_object":
                # Get type data from the form
                type_value = element_info["type"].get()
                
                # Create work type object
                type_data = {
                    "type": type_value
                }
                
                # Update type in the response_text
                self.json_data["response_text"]["type"] = type_data
                
            # Special handling for author object
            elif element_info.get("type") == "author_object":
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
                
        # We no longer have university_entries in the new data structure
        # so that part has been removed
        
        # Special handling for examination - the new structure has a single examination
        # rather than a list of examinations
        if hasattr(self, 'examination_entries') and self.examination_entries:
            # Get the first examination entry (since we now only have one examination)
            exam_entry = self.examination_entries[0]
            place = exam_entry["location"].get() if "location" in exam_entry else ""
            year_str = exam_entry["count"].get() if "count" in exam_entry else "0"
            
            try:
                year = int(year_str)
            except ValueError:
                year = 0
                
            # Only add if we have a place (required field)
            if place.strip():
                # Ensure the examination object exists
                if "examination" not in self.json_data["response_text"]:
                    self.json_data["response_text"]["examination"] = {}
                
                # Update examination
                self.json_data["response_text"]["examination"]["place"] = place
                self.json_data["response_text"]["examination"]["year"] = year
        
        # Special handling for library_reference
        if hasattr(self, 'library_reference_entry') and self.library_reference_entry:
            # Get the library reference entry
            shelfmark = self.library_reference_entry["shelfmark"].get() if "shelfmark" in self.library_reference_entry else ""
            publication_number = self.library_reference_entry["publication_number"].get() if "publication_number" in self.library_reference_entry else ""
            subjects = self.library_reference_entry["subjects"].get() if "subjects" in self.library_reference_entry else ""
            

            # Ensure the library_reference object exists
            if "library_reference" not in self.json_data["response_text"]:
                self.json_data["response_text"]["library_reference"] = {}
            
            # Update library_reference
            self.json_data["response_text"]["library_reference"]["shelfmark"] = shelfmark
            self.json_data["response_text"]["library_reference"]["publication_number"] = publication_number
            self.json_data["response_text"]["library_reference"]["subjects"] = subjects
        
        # Handle all other form elements based on their paths
        for path, element_info in self.form_elements.items():
            # Skip specially handled types
            if element_info.get("type") in ["work_type_object", "author_object", "university_list", "examinations_list", "examination_object", "library_reference_object"]:
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
    
    def save_json(self, show_message=False):
        """Save the JSON data to file."""
        if not self.json_data:
            if show_message:
                messagebox.showwarning("Warning", "No JSON data to save.")
            return
            
        try:
            # Update JSON data from form
            self.update_json_from_form()
            
            # Determine the appropriate JSON filename based on the image
            json_filename = None
            
            # If we have a current image path, use that to build the JSON filename
            if self.current_image_path:
                # Extract just the image basename without path or extension
                image_basename = os.path.basename(os.path.splitext(self.current_image_path)[0])
                # Apply the configured prefix only to the output file
                json_filename = f"{self.config.prefix}{image_basename}.json"
            # If we don't have an image but have a JSON path
            elif self.current_json_path:
                # Extract original JSON basename
                original_json_basename = os.path.basename(self.current_json_path)
                
                # Try to extract image name if original follows prefix pattern
                if self.is_json_with_prefix(original_json_basename):
                    # Get the original name without prefix
                    original_name = self.remove_prefix_from_json(original_json_basename)
                    # Apply the new prefix
                    json_filename = f"{self.config.prefix}{original_name}"
                else:
                    # Keep the original name if not following prefix pattern
                    json_filename = original_json_basename
            else:
                # This shouldn't happen, but just in case
                if show_message:
                    messagebox.showerror("Error", "No image or JSON file is loaded, cannot determine where to save.")
                return
            
            # Always enforce saving to the output directory if configured
            if self.config.output_dir:
                # Make sure the output directory exists
                os.makedirs(self.config.output_dir, exist_ok=True)
                output_path = os.path.join(self.config.output_dir, json_filename)
                self.logger.info(f"Saving JSON to output directory: {output_path}")
            else:
                # If no output directory specified, prompt the user to select one
                if show_message:
                    result = messagebox.askquestion("No Output Directory", 
                                                "No output directory configured. Would you like to select one now?")
                    if result == 'yes':
                        # Let user select output directory
                        output_dir = filedialog.askdirectory(title="Select Output Directory")
                        if output_dir:
                            # Update config and save the setting
                            self.config.output_dir = output_dir
                            self.output_dir_var.set(output_dir)
                            self.config.save_config()  # Save this setting for future use
                            os.makedirs(output_dir, exist_ok=True)
                            output_path = os.path.join(output_dir, json_filename)
                        else:
                            # User canceled directory selection
                            self.logger.warning("User canceled output directory selection")
                            return
                    else:
                        # Create a temporary output directory if they don't want to select one
                        temp_output_dir = os.path.join(os.getcwd(), "output")
                        os.makedirs(temp_output_dir, exist_ok=True)
                        output_path = os.path.join(temp_output_dir, json_filename)
                        self.logger.info(f"No output directory configured, using temporary output directory: {temp_output_dir}")
                        
                        # Show a warning
                        messagebox.showwarning("Using Temporary Output Directory", 
                                           f"Saving to temporary directory:\n{temp_output_dir}\n\n"
                                           f"It's recommended to configure a permanent output directory in the settings.")
                      
            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.json_data, f, indent=4)
                
            # Update the current JSON path to point to the saved location
            self.current_json_path = output_path
            self.json_label.config(text=f"JSON: {os.path.basename(output_path)}")
                
            if show_message:
                messagebox.showinfo("Success", f"JSON saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving: {str(e)}", exc_info=True)
            if show_message:
                messagebox.showerror("Error", f"Failed to save JSON: {str(e)}")
                
    def is_json_with_prefix(self, filename):
        """Check if a JSON filename follows the pattern of having a prefix."""
        return filename.lower().endswith('.json') and self.config.prefix in filename
        
    def remove_prefix_from_json(self, filename):
        """Remove the prefix from a JSON filename and return the base name."""
        if not filename.lower().endswith('.json'):
            return filename
            
        base_name = os.path.splitext(filename)[0]  # Remove .json extension
        if base_name.startswith(self.config.prefix):
            return base_name[len(self.config.prefix):]  # Remove prefix
        return base_name

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Ground Truther - image and JSON metadata editor')
    parser.add_argument('--image-dir', help='Directory containing images')
    parser.add_argument('--json-dir', help='Directory containing input JSON files')
    parser.add_argument('--output-dir', help='Directory where JSON files will be saved')
    parser.add_argument('--prefix', help='Prefix for JSON files (default: request_T66_)')
    parser.add_argument('--reset-config', action='store_true', help='Reset saved configuration')
    args = parser.parse_args()
    
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
    logger = logging.getLogger(__name__)
    
    # Create initial configuration
    config = Config(
        image_dir=args.image_dir,
        json_dir=args.json_dir,
        output_dir=args.output_dir,
        prefix=args.prefix if args.prefix else "request_T66_"
    )
    
    # If reset requested, don't load saved config
    if not args.reset_config:
        # Load saved configuration
        if config.load_config():
            logger.info("Loaded saved configuration")
        else:
            logger.info("No saved configuration found or error loading configuration")
    else:
        logger.info("Configuration reset requested - using command line arguments only")
        # Save the new config immediately to overwrite any previous one
        config.save_config()
    
    # Validate directories
    if config.image_dir and not os.path.isdir(config.image_dir):
        logger.warning(f"Image directory does not exist: {config.image_dir}")
        print(f"Warning: Image directory does not exist: {config.image_dir}")
        config.image_dir = None
        
    if config.json_dir and not os.path.isdir(config.json_dir):
        logger.warning(f"JSON directory does not exist: {config.json_dir}")
        print(f"Warning: JSON directory does not exist: {config.json_dir}")
        config.json_dir = None
        
    if config.output_dir and not os.path.isdir(config.output_dir):
        logger.warning(f"Output directory does not exist: {config.output_dir}")
        print(f"Warning: Output directory does not exist: {config.output_dir}, will create it when saving.")
    
    # Log configuration
    logger.info(f"Starting with configuration:")
    logger.info(f"  Image directory: {config.image_dir}")
    logger.info(f"  JSON directory: {config.json_dir}")
    logger.info(f"  Output directory: {config.output_dir}")
    logger.info(f"  JSON prefix: {config.prefix}")
    
    root = tk.Tk()
    
    # Initialize the app with our configuration
    app = MetadataEditor(root, config)
    
    # Add keyboard shortcuts
    # root.bind('<Right>', lambda event: app.next_image())
    # root.bind('<Left>', lambda event: app.previous_image())
    root.bind('<Control-s>', lambda event: app.save_json())
    
    # Try to load initial data
    initial_data_loaded = False
    
    # First priority: If image directory is specified, try to load the first image
    if config.image_dir and os.path.isdir(config.image_dir):
        app.update_images_in_folder()
        if app.images_in_folder:
            app.load_image(app.images_in_folder[0])
            initial_data_loaded = True
    
    # Second priority: If json directory is specified but no image loaded, try to load the first JSON
    if not initial_data_loaded and config.json_dir and os.path.isdir(config.json_dir):
        json_files = [f for f in os.listdir(config.json_dir) if f.lower().endswith('.json')]
        if json_files:
            json_files.sort()
            first_json_path = os.path.join(config.json_dir, json_files[0])
            app.current_json_path = first_json_path
            app.json_label.config(text=f"JSON: {os.path.basename(first_json_path)}")
            app.load_json()
            
            # Try to find matching image
            json_basename = os.path.basename(first_json_path)
            if json_basename.startswith(config.prefix):
                image_name = json_basename.replace(config.prefix, "").replace(".json", "")
                app.logger.info(f"Looking for image matching JSON: {image_name}")
                
                if config.image_dir and os.path.isdir(config.image_dir):
                    # Check for any image with that basename in the image dir
                    image_files = [f for f in os.listdir(config.image_dir) 
                                  if os.path.splitext(f)[0] == image_name]
                    if image_files:
                        image_path = os.path.join(config.image_dir, image_files[0])
                        app.current_image_path = image_path
                        app.image_label.config(text=f"Image: {os.path.basename(image_path)}")
                        app.display_image()
                        app.update_images_in_folder()
    
    # Handle window closing - save config on exit
    def on_closing():
        app.logger.info("Application closing, saving configuration")
        config.save_config()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Set the window size and position
    root.geometry("1200x800")
    root.update_idletasks()  # Update to get accurate window dimensions
    
    # Center the window on the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 1200) // 2
    y = (screen_height - 800) // 2
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()