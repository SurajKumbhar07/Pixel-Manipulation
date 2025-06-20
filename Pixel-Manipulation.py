import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk
import os
import threading
import time

class ImageEncryptor:
    def __init__(self):
        self.methods = {
            'xor': self._xor_encrypt,
            'shift': self._shift_encrypt,
            'shuffle': self._shuffle_encrypt,
            'invert': self._invert_encrypt
        }
    
    def encrypt(self, input_path, output_path, key, method='xor'):
        if method not in self.methods:
            raise ValueError(f"Unknown encryption method: {method}")
        
        img = Image.open(input_path)
        img_array = np.array(img)
        
        encrypted_array = self.methods[method](img_array, key)
        
        encrypted_img = Image.fromarray(encrypted_array)
        encrypted_img.save(output_path)
        
        return f"Image encrypted successfully using {method} method"
    
    def decrypt(self, input_path, output_path, key, method='xor'):
        if method not in self.methods:
            raise ValueError(f"Unknown encryption method: {method}")
        
        if method == 'xor' or method == 'invert':
            return self.encrypt(input_path, output_path, key, method)
        elif method == 'shift':
            img = Image.open(input_path)
            img_array = np.array(img)
            decrypted_array = self._shift_encrypt(img_array, -key)
            decrypted_img = Image.fromarray(decrypted_array)
            decrypted_img.save(output_path)
            return f"Image decrypted successfully using {method} method"
        elif method == 'shuffle':
            img = Image.open(input_path)
            img_array = np.array(img)
            decrypted_array = self._shuffle_decrypt(img_array, key)
            decrypted_img = Image.fromarray(decrypted_array)
            decrypted_img.save(output_path)
            return f"Image decrypted successfully using {method} method"
    
    def _xor_encrypt(self, img_array, key):
        height, width, channels = img_array.shape if len(img_array.shape) == 3 else (*img_array.shape, 1)
        
        np.random.seed(key)
        key_pattern = np.random.randint(0, 256, size=(height, width, channels if len(img_array.shape) == 3 else 1))
        
        if len(img_array.shape) == 3:
            return img_array.astype(np.uint8) ^ key_pattern.astype(np.uint8)
        else:
            return img_array.astype(np.uint8) ^ key_pattern[:,:,0].astype(np.uint8)
    
    def _shift_encrypt(self, img_array, key):
        return np.uint8((img_array.astype(np.int16) + key) % 256)
    
    def _shuffle_encrypt(self, img_array, key):
        height, width = img_array.shape[:2]
        
        flat_img = img_array.reshape(-1, *img_array.shape[2:] if len(img_array.shape) > 2 else 1)
        
        np.random.seed(key)
        indices = np.arange(flat_img.shape[0])
        np.random.shuffle(indices)
        
        shuffled_img = flat_img.copy()
        for i, idx in enumerate(indices):
            shuffled_img[idx] = flat_img[i]
        
        if len(img_array.shape) > 2:
            return shuffled_img.reshape(height, width, -1)
        else:
            return shuffled_img.reshape(height, width)
    
    def _shuffle_decrypt(self, img_array, key):
        height, width = img_array.shape[:2]
        
        flat_img = img_array.reshape(-1, *img_array.shape[2:] if len(img_array.shape) > 2 else 1)
        
        np.random.seed(key)
        indices = np.arange(flat_img.shape[0])
        np.random.shuffle(indices)
        
        unshuffled_img = flat_img.copy()
        for i, idx in enumerate(indices):
            unshuffled_img[i] = flat_img[idx]
        
        if len(img_array.shape) > 2:
            return unshuffled_img.reshape(height, width, -1)
        else:
            return unshuffled_img.reshape(height, width)
    
    def _invert_encrypt(self, img_array, key):
        np.random.seed(key)
        
        if len(img_array.shape) == 3:
            height, width, channels = img_array.shape
            invert_channels = np.random.choice([True, False], size=channels)
            
            result = img_array.copy()
            for c in range(channels):
                if invert_channels[c]:
                    result[:,:,c] = 255 - result[:,:,c]
            
            return result
        else:
            return 255 - img_array

class ImageEncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Encryption Tool")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        self.input_path = ""
        self.output_path = ""
        self.encryptor = ImageEncryptor()
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        control_frame = ttk.LabelFrame(paned_window, text="Controls", padding="10")
        paned_window.add(control_frame, weight=1)
        
        preview_frame = ttk.LabelFrame(paned_window, text="Image Preview", padding="10")
        paned_window.add(preview_frame, weight=2)
        
        self.setup_control_panel(control_frame)
        
        self.setup_preview_panel(preview_frame)
    
    def setup_control_panel(self, parent):
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="Input Image:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.input_entry = ttk.Entry(file_frame, width=30)
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=(5, 5), pady=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_input).grid(row=0, column=2, pady=(0, 5))
        
        ttk.Label(file_frame, text="Output Image:").grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.output_entry = ttk.Entry(file_frame, width=30)
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=(5, 5), pady=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, pady=(0, 5))
        
        file_frame.columnconfigure(1, weight=1)
        
        settings_frame = ttk.LabelFrame(parent, text="Encryption Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(settings_frame, text="Encryption Key:").grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.key_entry = ttk.Entry(settings_frame, width=20)
        self.key_entry.grid(row=0, column=1, sticky="ew", pady=(0, 10))
        self.key_entry.insert(0, "123456")
        
        ttk.Label(settings_frame, text="Encryption Method:").grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.method_var = tk.StringVar(value="xor")
        
        method_frame = ttk.Frame(settings_frame)
        method_frame.grid(row=2, column=0, columnspan=2, sticky="w")
        
        methods = [
            ("XOR", "xor"),
            ("Shift", "shift"),
            ("Shuffle", "shuffle"),
            ("Invert", "invert")
        ]
        
        for i, (text, value) in enumerate(methods):
            ttk.Radiobutton(
                method_frame, 
                text=text, 
                value=value, 
                variable=self.method_var
            ).grid(row=0, column=i, padx=(0, 10))
        
        settings_frame.columnconfigure(1, weight=1)
        
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="Encrypt", 
            command=self.encrypt,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        ttk.Button(
            button_frame, 
            text="Decrypt", 
            command=self.decrypt,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))
        
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack(anchor="w")
    
    def setup_preview_panel(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.original_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.original_frame, text="Original Image")
        
        self.result_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.result_frame, text="Result Image")
        
        self.original_canvas = tk.Canvas(self.original_frame, bg="white")
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.result_canvas = tk.Canvas(self.result_frame, bg="white")
        self.result_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.display_default_image(self.original_canvas, "No original image selected")
        self.display_default_image(self.result_canvas, "No result image yet")
    
    def display_default_image(self, canvas, message):
        canvas.delete("all")
        canvas.create_text(
            canvas.winfo_width() // 2 or 200,
            canvas.winfo_height() // 2 or 150,
            text=message,
            fill="gray",
            font=("Arial", 12)
        )
    
    def display_image(self, canvas, path):
        try:
            img = Image.open(path)
            
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            if canvas_width < 10 or canvas_height < 10:
                canvas_width = 400
                canvas_height = 400
            
            img_width, img_height = img.size
            ratio = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            
            if not hasattr(self, 'photo_images'):
                self.photo_images = {}
            
            photo_img = ImageTk.PhotoImage(img_resized)
            self.photo_images[canvas] = photo_img
            
            canvas.delete("all")
            canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                image=photo_img,
                anchor=tk.CENTER
            )
            
            info_text = f"Size: {img_width}x{img_height} | Format: {img.format}"
            canvas.create_text(
                10,
                canvas_height - 10,
                text=info_text,
                anchor="sw",
                fill="black",
                font=("Arial", 8)
            )
            
        except Exception as e:
            canvas.delete("all")
            canvas.create_text(
                canvas.winfo_width() // 2 or 200,
                canvas.winfo_height() // 2 or 150,
                text=f"Error displaying image: {str(e)}",
                fill="red",
                font=("Arial", 10)
            )
    
    def browse_input(self):
        self.input_path = filedialog.askopenfilename(
            title="Select Input Image",
            filetypes=[
                ("PNG files", "*.png"), 
                ("JPEG files", "*.jpg *.jpeg"), 
                ("BMP files", "*.bmp"),
                ("GIF files", "*.gif"),
                ("All files", "*.*")
            ]
        )
        
        if self.input_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.input_path)
            
            self.display_image(self.original_canvas, self.input_path)
            
            directory = os.path.dirname(self.input_path)
            filename = os.path.basename(self.input_path)
            name, ext = os.path.splitext(filename)
            self.output_path = os.path.join(directory, f"{name}_processed{ext}")
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.output_path)
            
            self.notebook.select(0)
    
    def browse_output(self):
        self.output_path = filedialog.asksaveasfilename(
            title="Save Output Image",
            filetypes=[
                ("PNG files", "*.png"), 
                ("JPEG files", "*.jpg"), 
                ("BMP files", "*.bmp"),
                ("All files", "*.*")
            ],
            defaultextension=".png"
        )
        
        if self.output_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.output_path)
    
    def get_parameters(self):
        input_path = self.input_entry.get()
        output_path = self.output_entry.get()
        method = self.method_var.get()
        
        try:
            key = int(self.key_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Encryption key must be a number")
            return None, None, None, None
        
        if not input_path:
            messagebox.showerror("Error", "Please select an input image")
            return None, None, None, None
        
        if not output_path:
            messagebox.showerror("Error", "Please specify an output location")
            return None, None, None, None
        
        return input_path, output_path, key, method
    
    def encrypt(self):
        params = self.get_parameters()
        if params[0] is None:
            return
        
        self.status_label.config(text="Encrypting...")
        self.progress_var.set(0)
        
        threading.Thread(target=self._encrypt_thread, args=params, daemon=True).start()
    
    def decrypt(self):
        params = self.get_parameters()
        if params[0] is None:
            return
        
        self.status_label.config(text="Decrypting...")
        self.progress_var.set(0)
        
        threading.Thread(target=self._decrypt_thread, args=params, daemon=True).start()
    
    def _encrypt_thread(self, input_path, output_path, key, method):
        try:
            for i in range(0, 91, 10):
                self.progress_var.set(i)
                time.sleep(0.05)
            
            result = self.encryptor.encrypt(input_path, output_path, key, method)
            
            self.progress_var.set(100)
            
            self.root.after(0, lambda: self._complete_operation(output_path, result))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self._show_error(error_msg))
    
    def _decrypt_thread(self, input_path, output_path, key, method):
        try:
            for i in range(0, 91, 10):
                self.progress_var.set(i)
                time.sleep(0.05)
            
            result = self.encryptor.decrypt(input_path, output_path, key, method)
            
            self.progress_var.set(100)
            
            self.root.after(0, lambda: self._complete_operation(output_path, result))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self._show_error(error_msg))
    
    def _complete_operation(self, output_path, result):
        self.status_label.config(text="Complete")
        messagebox.showinfo("Success", result)
        
        self.display_image(self.result_canvas, output_path)
        
        self.notebook.select(1)
    
    def _show_error(self, error_msg):
        self.status_label.config(text=f"Error: {error_msg}")
        self.progress_var.set(0)
        messagebox.showerror("Error", error_msg)

def setup_styles():
    style = ttk.Style()
    
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    
    style.configure("Accent.TButton", font=("Arial", 10, "bold"))
    
    style.configure("TLabelframe", borderwidth=2)
    style.configure("TLabelframe.Label", font=("Arial", 10, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    setup_styles()
    app = ImageEncryptionApp(root)
    root.mainloop() 
