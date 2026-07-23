import tkinter as tk
import threading
from stt import process_voice_command

class RobotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pet Assistant")
        
        # State flags GUI
        self.chat_visible = True
        self.dragged = False
        self.expanded_width = 450
        self.expanded_height = 380
        self.collapsed_width = 120
        
        # Remove window decorations (frameless)
        self.root.overrideredirect(True)
        
        # Set transparency
        # Use a specific color that will be treated as transparent
        self.bg_color = '#abcdef' # A rare color
        self.root.config(bg=self.bg_color)
        self.root.wm_attributes("-transparentcolor", self.bg_color)
        
        # Make the window stay on top
        self.root.attributes("-topmost", True)

        # Main horizontal container
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # -------------------------------------------------------------
        # CAT PANEL (Right side, Transparent background)
        # Pack CAT PANEL first to give it the highest layout priority
        # -------------------------------------------------------------
        self.cat_frame = tk.Frame(self.main_container, bg=self.bg_color)
        self.cat_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=10, pady=10)

        # -------------------------------------------------------------
        # CHAT PANEL (Left side, Solid Elegant Dark Theme)
        # -------------------------------------------------------------
        self.chat_frame = tk.Frame(self.main_container, bg='#1e1e2e', bd=2, relief=tk.FLAT)
        self.chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)

        # Handle resize tipis di sisi kiri chat_frame
        self.resize_left = tk.Frame(self.chat_frame, width=4, cursor="sb_h_double_arrow", bg='#1e1e2e')
        self.resize_left.pack(side=tk.LEFT, fill=tk.Y)
        self.resize_left.bind("<Button-1>", self.start_resize_left)
        self.resize_left.bind("<B1-Motion>", self.do_resize_left)

        # Handle resize tipis di sisi atas chat_frame
        self.resize_top = tk.Frame(self.chat_frame, height=4, cursor="sb_v_double_arrow", bg='#1e1e2e')
        self.resize_top.pack(side=tk.TOP, fill=tk.X)
        self.resize_top.bind("<Button-1>", self.start_resize_top)
        self.resize_top.bind("<B1-Motion>", self.do_resize_top)

        # Header Frame for chat panel
        self.header_frame = tk.Frame(self.chat_frame, bg="#1e1e2e")
        self.header_frame.pack(fill=tk.X, pady=(10, 5), padx=10)

        self.header_label = tk.Label(
            self.header_frame, 
            text="🐈 Pet Assistant Chat", 
            fg="#cdd6f4", 
            bg="#1e1e2e", 
            font=("Segoe UI", 11, "bold")
        )
        self.header_label.pack(side=tk.LEFT)

        # Reset button
        self.reset_button = tk.Button(
            self.header_frame,
            text="🔄 Reset",
            bg="#f38ba8", # Pastel red/pink from Catppuccin Mocha
            fg="#11111b",
            font=("Segoe UI", 8, "bold"),
            activebackground="#f9e2af",
            activeforeground="#11111b",
            bd=0,
            padx=8,
            pady=2,
            command=self.reset_chat
        )
        self.reset_button.pack(side=tk.RIGHT)

        # Chat history display
        self.chat_history = tk.Text(
            self.chat_frame, 
            bg="#181825", 
            fg="#cdd6f4", 
            insertbackground="white", 
            font=("Segoe UI", 10), 
            wrap=tk.WORD, 
            height=8, 
            width=35, 
            state=tk.DISABLED, 
            bd=0
        )
        self.chat_history.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Status indicator
        self.status_label = tk.Label(
            self.chat_frame, 
            text="Status: Idle", 
            fg="#a6adc8", 
            bg="#1e1e2e", 
            font=("Segoe UI", 9, "italic")
        )
        self.status_label.pack(pady=(2, 5), padx=10, anchor="w")

        # Input Frame for typing queries
        self.input_frame = tk.Frame(self.chat_frame, bg='#1e1e2e')
        self.input_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # Text Entry field
        self.query_entry = tk.Entry(
            self.input_frame, 
            bg="#181825", 
            fg="#cdd6f4", 
            insertbackground="white", 
            font=("Segoe UI", 10), 
            bd=0
        )
        self.query_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=6, padx=(0, 5))
        self.query_entry.bind("<Return>", lambda e: self.send_typed_query())
        
        # Send Button
        self.send_button = tk.Button(
            self.input_frame, 
            text="✉️ Kirim", 
            bg="#a6e3a1", 
            fg="#11111b", 
            font=("Segoe UI", 9, "bold"), 
            activebackground="#b4befe", 
            activeforeground="#11111b", 
            bd=0, 
            padx=10, 
            command=self.send_typed_query
        )
        self.send_button.pack(side=tk.RIGHT, fill=tk.Y)

        # Speak Button
        self.mic_button = tk.Button(
            self.chat_frame, 
            text="🎤 Tanya Asisten", 
            bg="#89b4fa", 
            fg="#11111b", 
            font=("Segoe UI", 10, "bold"), 
            activebackground="#b4befe", 
            activeforeground="#11111b", 
            bd=0, 
            padx=10, 
            pady=5, 
            command=self.start_voice_thread
        )
        self.mic_button.pack(padx=10, pady=(5, 10), fill=tk.X)

        # Load animated GIF
        self.img_path = "orange-cat.gif"
        self.frames = []
        self.frame_index = 0
        
        try:
            # Load all frames of the GIF
            frame_idx = 0
            while True:
                try:
                    # Tkinter PhotoImage can load specific frames of a GIF
                    frame = tk.PhotoImage(file=self.img_path, format=f"gif -index {frame_idx}").subsample(5,5)
                    self.frames.append(frame)
                    frame_idx += 1
                except tk.TclError:
                    break # No more frames
            
            if not self.frames:
                raise Exception("No frames found in GIF")
                
            self.image = self.frames[0]
        except Exception as e:
            print(f"Error loading animated GIF: {e}")
            # Fallback to a simple label if image fails
            self.label = tk.Label(self.cat_frame, text="Cat Error", bg=self.bg_color)
            self.label.pack()
            return

        # Create label to hold the image
        self.label = tk.Label(self.cat_frame, image=self.image, bg=self.bg_color)
        self.label.pack(side=tk.BOTTOM) # Kucing sejajar di bawah (bottom-aligned)

        # Drag window by clicking and holding the cat
        self.label.bind("<Button-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.do_move)
        self.label.bind("<ButtonRelease-1>", self.stop_move)
        
        # Binding for exit (Esc key)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Start animation loop
        self.update_animation()

        # Position the window in the bottom right corner
        self.root.update_idletasks()
        w = self.expanded_width
        h = self.expanded_height
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate coordinates for bottom right with a 20px margin
        margin = 20
        x = screen_width - w - margin
        y = screen_height - h - margin - 40 # Extra offset for taskbar usually
        
        self.root.geometry(f'{w}x{h}+{x}+{y}')
        
        # Lift cat frame to top visual layer
        self.cat_frame.lift()

    def update_animation(self):
        """Cycle through GIF frames."""
        if not self.frames:
            return
            
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.label.configure(image=self.frames[self.frame_index])
        # Update every 100ms (adjust for GIF speed)
        self.root.after(100, self.update_animation)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y
        self.dragged = False

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        if abs(deltax) > 3 or abs(deltay) > 3:
            self.dragged = True
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def stop_move(self, event):
        if not self.dragged:
            self.toggle_chat()

    def toggle_chat(self):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        
        if self.chat_visible:
            # Save current size before hiding
            self.expanded_width = self.root.winfo_width()
            self.expanded_height = self.root.winfo_height()
            
            # Hide the chat panel
            self.chat_frame.pack_forget()
            
            # Calculate new X position so the cat stays in the same place
            new_x = x + self.expanded_width - self.collapsed_width
            self.root.geometry(f"{self.collapsed_width}x{self.expanded_height}+{new_x}+{y}")
            self.chat_visible = False
        else:
            # Repack: cat first, then chat to preserve layout priority
            self.cat_frame.pack_forget()
            self.cat_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=10, pady=10)
            # Show the chat panel
            self.chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
            
            # Restore to original size, moving X to the left
            new_x = x - (self.expanded_width - self.collapsed_width)
            self.root.geometry(f"{self.expanded_width}x{self.expanded_height}+{new_x}+{y}")
            self.chat_visible = True
            
            # Lift cat frame to top visual layer
            self.cat_frame.lift()

    # --- Thread-Safe UI Update Functions ---
    def update_chat(self, sender, text):
        self.root.after(0, self._safe_update_chat, sender, text)

    def _safe_update_chat(self, sender, text):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"💬 {sender}:\n{text}\n\n")
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)

    def update_status(self, status_text):
        self.root.after(0, lambda: self.status_label.config(text=f"Status: {status_text}"))

    # --- Threading & Resize Logic ---
    def start_resize_left(self, event):
        self.resize_start_x = event.x_root
        self.window_start_x = self.root.winfo_x()
        self.window_start_width = self.root.winfo_width()

    def do_resize_left(self, event):
        deltax = event.x_root - self.resize_start_x
        new_width = self.window_start_width - deltax
        new_x = self.window_start_x + deltax
        # Enforce reasonable minimum width
        if new_width >= 350:
            self.root.geometry(f"{new_width}x{self.root.winfo_height()}+{new_x}+{self.root.winfo_y()}")

    def start_resize_top(self, event):
        self.resize_start_y = event.y_root
        self.window_start_y = self.root.winfo_y()
        self.window_start_height = self.root.winfo_height()

    def do_resize_top(self, event):
        deltay = event.y_root - self.resize_start_y
        new_height = self.window_start_height - deltay
        new_y = self.window_start_y + deltay
        # Enforce reasonable minimum height
        if new_height >= 250:
            self.root.geometry(f"{self.root.winfo_width()}x{new_height}+{self.root.winfo_x()}+{new_y}")

    def send_typed_query(self):
        query = self.query_entry.get().strip()
        if not query:
            return
        
        # Clear the input field
        self.query_entry.delete(0, tk.END)
        
        # Display user query in chat
        self.update_chat("Anda", query)
        
        # Disable interaction buttons
        self.send_button.config(state=tk.DISABLED)
        self.mic_button.config(state=tk.DISABLED)
        
        # Process request in a separate thread to keep UI responsive
        threading.Thread(target=self.run_text_interaction, args=(query,), daemon=True).start()

    def run_text_interaction(self, query):
        try:
            self.update_status("🤖 Berpikir...")
            import gemini_brain
            response_text = gemini_brain.send_prompt_request(query)
            self.update_chat("Asisten", response_text)
        except Exception as e:
            self.update_chat("Sistem Error", str(e))
        finally:
            # Re-enable buttons and set status back to Idle
            self.root.after(0, lambda: self.send_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.mic_button.config(state=tk.NORMAL))
            self.update_status("Idle")

    def start_voice_thread(self):
        # Disable buttons to prevent multiple simultaneous processes
        self.mic_button.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        threading.Thread(target=self.run_voice_interaction, daemon=True).start()

    def run_voice_interaction(self):
        try:
            process_voice_command(
                update_gui_callback=self.update_chat,
                update_status_callback=self.update_status,
                adjust_duration=0.5  # Faster response
            )
        except Exception as e:
            self.update_chat("Sistem Error", str(e))
        finally:
            # Re-enable voice button, send button, and reset status
            self.root.after(0, lambda: self.mic_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.send_button.config(state=tk.NORMAL))
            self.update_status("Idle")

    def reset_chat(self):
        """Mereset session chat di Gemini dan membersihkan layar GUI."""
        try:
            import gemini_brain
            gemini_brain.reset_chat_session()
            
            # Bersihkan chat history di GUI
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.delete(1.0, tk.END)
            self.chat_history.insert(tk.END, "✨ Chat direset. Topik baru dimulai!\n\n")
            self.chat_history.config(state=tk.DISABLED)
            
            self.update_status("Chat direset")
            
            # Kosongkan entry input jika ada teks yang belum terkirim
            self.query_entry.delete(0, tk.END)
        except Exception as e:
            self.update_chat("Sistem Error", f"Gagal mereset chat: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotApp(root)
    root.mainloop()
