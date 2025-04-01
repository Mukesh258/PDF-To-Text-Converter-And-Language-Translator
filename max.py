import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
from deep_translator import GoogleTranslator
import pdfplumber
import os
from datetime import datetime
import threading
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit

class ModernPDFTranslator:
    def __init__(self):
        # Set appearance mode and default color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("TransPDF Pro")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.recent_files = []
        self.max_recent_files = 5
        
        # Create UI elements
        self.create_sidebar()
        self.create_main_content()
        
    def create_sidebar(self):
        # Sidebar frame
        self.sidebar = ctk.CTkFrame(self.root, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        
        # Logo/Brand
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="TransPDF Pro",
            font=("Helvetica", 20, "bold"),
            text_color=("#3498db", "#2980b9")
        )
        self.logo_label.pack(pady=20, padx=20)
        
        # Navigation buttons
        nav_items = [
            ("Upload PDF", self.show_upload_section),
            ("Recent Files", self.show_recent_files)
        ]
        
        for text, command in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                font=("Helvetica", 14),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                anchor="w",
                width=200,
                height=40
            )
            btn.pack(pady=5, padx=20)
            
    def create_main_content(self):
        # Main content area
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        self.show_upload_section()
        
    def show_upload_section(self):
        self.clear_main_frame()
        
        # Upload frame
        upload_frame = ctk.CTkFrame(self.main_frame)
        upload_frame.pack(fill="both", expand=True)
        
        # Title
        title = ctk.CTkLabel(
            upload_frame,
            text="Upload your PDF",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=20)
        
        # Upload zone
        drop_zone = ctk.CTkFrame(
            upload_frame,
            fg_color=("gray85", "gray25"),
            corner_radius=10
        )
        drop_zone.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Upload icon and label
        drop_label = ctk.CTkLabel(
            drop_zone,
            text="Drag & Drop PDF here\nor",
            font=("Helvetica", 18)
        )
        drop_label.pack(pady=(100, 10))
        
        upload_btn = ctk.CTkButton(
            drop_zone,
            text="Choose File",
            command=self.upload_pdf,
            font=("Helvetica", 15),
            width=200,
            height=40
        )
        upload_btn.pack(pady=10)
        
    def upload_pdf(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF Files", "*.pdf")]
        )
        if file_path:
            self.process_pdf(file_path)
            
    def process_pdf(self, file_path):
        try:
            # Show loading progress
            progress = ctk.CTkProgressBar(
                self.main_frame,
                mode="indeterminate",
                width=300
            )
            progress.pack(pady=10)
            progress.start()
            
            # Process in thread to prevent UI freeze
            def process():
                try:
                    with pdfplumber.open(file_path) as pdf:
                        text = "\n".join([
                            page.extract_text() 
                            for page in pdf.pages 
                            if page.extract_text()
                        ])
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self.show_translation_window(text))
                    self.add_to_recent(file_path)
                except Exception as e:
                    self.root.after(0, lambda: self.show_error(str(e)))
                finally:
                    self.root.after(0, progress.destroy)
                    
            threading.Thread(target=process).start()
            
        except Exception as e:
            self.show_error(str(e))
            
    def show_translation_window(self, text):
        trans_window = ctk.CTkToplevel(self.root)
        trans_window.title("Translation")
        trans_window.geometry("1200x800")
        
        # Make window appear on top and center it
        trans_window.transient(self.root)
        trans_window.grab_set()
        
        # Center the window
        x = self.root.winfo_x() + (self.root.winfo_width() - 1200) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 800) // 2
        trans_window.geometry(f"1200x800+{x}+{y}")
        
        # Language selection
        lang_frame = ctk.CTkFrame(trans_window)
        lang_frame.pack(fill="x", padx=20, pady=10)
        
        lang_label = ctk.CTkLabel(
            lang_frame,
            text="Target Language:",
            font=("Helvetica", 14)
        )
        lang_label.pack(side="left", padx=10)
        
        languages = GoogleTranslator().get_supported_languages()
        lang_var = ctk.StringVar(value="english")
        
        lang_menu = ctk.CTkOptionMenu(
            lang_frame,
            values=languages,
            variable=lang_var,
            width=200
        )
        lang_menu.pack(side="left", padx=10)
        
        # Text areas with increased size
        text_frame = ctk.CTkFrame(trans_window)
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        text_frame.grid_columnconfigure((0, 1), weight=1)
        text_frame.grid_rowconfigure(0, weight=1)  # Make row expandable
        
        # Original text with increased size
        original_text = ctk.CTkTextbox(
            text_frame,
            font=("Helvetica", 12),
            wrap="word",
            height=600  # Increased height
        )
        original_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        original_text.insert("1.0", text)
        
        # Translated text with increased size
        translated_text = ctk.CTkTextbox(
            text_frame,
            font=("Helvetica", 12),
            wrap="word",
            height=600  # Increased height
        )
        translated_text.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Control buttons
        btn_frame = ctk.CTkFrame(trans_window)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        def translate():
            # Show progress
            progress = ctk.CTkProgressBar(
                btn_frame,
                mode="indeterminate",
                width=100
            )
            progress.pack(side="left", padx=5)
            progress.start()
            
            def translate_thread():
                try:
                    translator = GoogleTranslator(
                        source='auto',
                        target=lang_var.get()
                    )
                    
                    result = translator.translate(text)
                    
                    # Update UI in main thread
                    trans_window.after(0, lambda: translated_text.delete("1.0", "end"))
                    trans_window.after(0, lambda: translated_text.insert("1.0", result))
                    
                except Exception as e:
                    trans_window.after(0, lambda: self.show_error(str(e)))
                finally:
                    trans_window.after(0, progress.destroy)
                    
            threading.Thread(target=translate_thread).start()
            
        translate_btn = ctk.CTkButton(
            btn_frame,
            text="Translate",
            command=translate,
            width=120
        )
        translate_btn.pack(side="left", padx=5)
        
        # Copy button
        def copy():
            self.root.clipboard_clear()
            self.root.clipboard_append(translated_text.get("1.0", "end-1c"))
            messagebox.showinfo("Success", "Copied to clipboard!")
            
        copy_btn = ctk.CTkButton(
            btn_frame,
            text="Copy",
            command=copy,
            width=100
        )
        copy_btn.pack(side="left", padx=5)
        
        # Save button
        def save():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("Text files", "*.txt")]
            )
            if file_path:
                try:
                    if file_path.endswith('.pdf'):
                        self.save_as_pdf(
                            file_path,
                            original_text.get("1.0", "end-1c"),
                            translated_text.get("1.0", "end-1c")
                        )
                    else:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(translated_text.get("1.0", "end-1c"))
                    messagebox.showinfo("Success", "File saved successfully!")
                except Exception as e:
                    self.show_error(f"Failed to save: {str(e)}")
                    
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save",
            command=save,
            width=100
        )
        save_btn.pack(side="left", padx=5)
        
    def save_as_pdf(self, file_path, original_text, translated_text):
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "PDF Translation")
        
        # Original text
        y_position = height - 100
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Original Text:")
        
        c.setFont("Helvetica", 12)
        for line in simpleSplit(original_text, "Helvetica", 12, width - 100):
            y_position -= 20
            if y_position < 50:
                c.showPage()
                y_position = height - 50
            c.drawString(50, y_position, line)
            
        # Translated text
        y_position -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Translated Text:")
        
        c.setFont("Helvetica", 12)
        for line in simpleSplit(translated_text, "Helvetica", 12, width - 100):
            y_position -= 20
            if y_position < 50:
                c.showPage()
                y_position = height - 50
            c.drawString(50, y_position, line)
            
        c.save()
        
    def show_error(self, message):
        messagebox.showerror("Error", message)
        
    def add_to_recent(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files.pop()
            
    def show_recent_files(self):
        self.clear_main_frame()
        
        # Title
        title = ctk.CTkLabel(
            self.main_frame,
            text="Recent Files",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=20)
        
        if not self.recent_files:
            no_files = ctk.CTkLabel(
                self.main_frame,
                text="No recent files",
                font=("Helvetica", 14)
            )
            no_files.pack(pady=50)
            return
        
        # Create scrollable frame for recent files
        scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            width=800,
            height=600
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        for file_path in self.recent_files:
            # File frame
            file_frame = ctk.CTkFrame(scroll_frame)
            file_frame.pack(fill="x", pady=5, padx=5)
            
            # File name
            name_label = ctk.CTkLabel(
                file_frame,
                text=os.path.basename(file_path),
                font=("Helvetica", 12)
            )
            name_label.pack(side="left", padx=10, pady=10)
            
            # Open button
            open_btn = ctk.CTkButton(
                file_frame,
                text="Open",
                command=lambda f=file_path: self.process_pdf(f),
                width=100
            )
            open_btn.pack(side="right", padx=10, pady=5)
        
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = ModernPDFTranslator()
    app.root.mainloop()