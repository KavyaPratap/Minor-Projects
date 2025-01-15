#updates------->
#added undo redo, with ctrl z and ctrl y,-----successfully!!
#added image widget------successfully!!
#added save generated code in a python file------successfully!!
#redesigned file menu and add a quit option too-------successfully!!
#added treeview in show_recent files, now it looks more professional----successfully!!
#added custom theme color----successfully!!
#add treeview---------error-----when i right click i cant add or remove column row., also fine tune tree view rest is ok



#problems---------->
#still exist
#problem is-----1.when you delete the widget and undo that, the path of that widget gets deleted
#               2.you can't redo something thats deleted
#                3.When you add a function, generate code wont work



#------------------------------------CODE STARTS HERE------------------------------------#
import tkinter as tk
from tkinter import ttk, messagebox, filedialog,simpledialog
from tkinter import colorchooser
import json  # For saving and loading the layout
import os
import mysql.connector
from PIL import Image, ImageTk 
from datetime import datetime
from hand_mouse_controller import HandMouseController
class TkinterAppDesigner:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter App Designer")
        self.root.geometry("900x600")

        self.toolbar_visible = True
        self.create_menu()  # menu bar
        self.create_toolbar()
        self.create_canvas()
        # Keyboard shortcuts
        self.root.bind('<Control-s>', self.save_layout)
        self.root.bind('<Control-o>', self.load_layout)
        self.root.bind('<Control-g>', self.generate_code)
        self.root.bind('<Control-x>', self.clear_all_widgets)
        self.root.bind('<Control-z>', self.undo_action) 
        self.root.bind('<Control-y>', self.redo_action)  

        self.widgets = []
        self.widget_ids = {}
        self.widget_functions = {}
        self.function_states = {}
        self.undo_stack = []  
        self.redo_stack = [] 
        self.long_click_timer = None
        self.double_click_timer = None
        self.double_click_delay = 300
        self.long_click_duration = 2000

        # Initialize drag and resize state
        self.dragging_widget = None
        self.resizing = False
        self.resize_direction = None
        self.offset_x = 0
        self.offset_y = 0
        #adding database
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="recentfiles"
        )
        self.cursor = self.db.cursor()

    def close_database(self):
        self.cursor.close()
        self.db.close()

    def create_menu(self):
        # menu bar
        menubar = tk.Menu(self.root)

        # 'File' menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Recent", command=self.show_recent_files)
        file_menu.add_command(label="New", command=self.new_canvas)
        file_menu.add_command(label="Clear All- CTRL+X", command=self.clear_all_widgets)
        file_menu.add_command(label="Save Layout- CTRL+S", command=self.save_layout)
        file_menu.add_command(label="Load Layout- CTRL+o", command=self.load_layout)
        file_menu.add_command(label="Undo- CTRL+Z", command=self.undo_action)
        file_menu.add_command(label="Redo- CTRL+Y", command=self.redo_action)
        file_menu.add_command(label="Generate Code- CTRL+G", command=self.generate_code)
        file_menu.add_command(label="Save Generated Code", command=self.save_generated_code)

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # 'Styles' menu
        styles_menu = tk.Menu(menubar, tearoff=0)
        styles_menu.add_command(label="Standard", command=lambda: self.apply_style("Standard"))
        styles_menu.add_command(label="Primary", command=lambda: self.apply_style("Primary"))
        styles_menu.add_command(label="Secondary", command=lambda: self.apply_style("Secondary"))
        styles_menu.add_command(label="Custom", command=self.custom_style)
        menubar.add_cascade(label="Select Style", menu=styles_menu)

        # Configuring menu bar
        self.root.config(menu=menubar)

    def apply_style(self, style):
        self.style_dropdown.set(style) 
    
    def custom_style(self):
        # Open a dialog for picking background color
        bg_color = colorchooser.askcolor(title="Pick Background Color")[1]
        if not bg_color:
            return  # User canceled the selection

        # Open a dialog for picking foreground color
        fg_color = colorchooser.askcolor(title="Pick Foreground Color")[1]
        if not fg_color:
            return  # User canceled the selection

        # Apply the custom colors to all selected widgets or prompt user for a target widget
        if not self.widgets:
            messagebox.showinfo("No Widgets", "No widgets to style. Add widgets first.")
            return

        for widget in self.widgets:
            widget_type = type(widget).__name__
            # Apply custom colors only to widgets that support bg/fg
            if widget_type in ["Button", "Label", "Entry", "Text"]:
                widget.config(bg=bg_color, fg=fg_color)
            elif widget_type == "Frame":
                widget.config(bg=bg_color)

        # Save custom colors for each widget for persistence
        for widget in self.widgets:
            self.record_custom_colors(widget, bg_color, fg_color)
        messagebox.showinfo("Custom Style", "Custom colors applied successfully!")

    def check_unsaved_changes(self):
        if self.widgets:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them before proceeding?"
            )
            if response:  # Yes
                self.save_layout()
            return response is not None  # None means Cancel
        return True  # No widgets, nothing to save

    def new_canvas(self):
        if self.check_unsaved_changes():
            self.clear_all_widgets()

    def update_recent_files(self, file_name, file_path):
        # Check if file already exists in the database
        query = "SELECT id FROM recent_files WHERE file_path = %s"
        self.cursor.execute(query, (file_path,))
        result = self.cursor.fetchone()

        if result:
            # Update the timestamp for existing file
            update_query = "UPDATE recent_files SET last_accessed = %s WHERE id = %s"
            self.cursor.execute(update_query, (datetime.now(), result[0]))
        else:
            # Insert new record
            insert_query = "INSERT INTO recent_files (file_name, file_path) VALUES (%s, %s)"
            self.cursor.execute(insert_query, (file_name, file_path))
        
        self.db.commit()
    
    def open_recent_file(self, file_path=None):
        if file_path is None:
            # Fetch the most recent file from the database
            query = "SELECT file_name, file_path FROM recent_files ORDER BY last_accessed DESC LIMIT 1"
            self.cursor.execute(query)
            recent_file = self.cursor.fetchone()

            if recent_file:
                file_name, file_path = recent_file
            else:
                messagebox.showinfo("No Recent Files", "No recent files found in the database.")
                return

        if os.path.exists(file_path):  # Check if the file still exists
            self.load_layout(file_path)  # Load the file directly
            messagebox.showinfo("Recent File", f"Opened file: {os.path.basename(file_path)}")
        else:
            messagebox.showerror("File Not Found", f"The file '{os.path.basename(file_path)}' no longer exists.")
            self.update_database()  # Clean up invalid entries

    def show_recent_files(self):
        # Create a new window for displaying recent files
        recent_window = tk.Toplevel(self.root)
        recent_window.title("Recent Files")
        recent_window.geometry("800x400")

        # Create a label at the top
        tk.Label(recent_window, text="Recent Files", font=("Arial", 16)).pack(pady=10)

        # Create a Treeview widget
        columns = ("File Name", "Date", "Path")
        tree = ttk.Treeview(recent_window, columns=columns, show="headings", height=15)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Define column headers
        tree.heading("File Name", text="File Name")
        tree.heading("Date", text="Date Last Accessed")
        tree.heading("Path", text="File Path")

        # Define column widths
        tree.column("File Name", width=200, anchor="w")
        tree.column("Date", width=150, anchor="center")
        tree.column("Path", width=400, anchor="w")

        # Fetch recent files from the database
        query = "SELECT file_name, file_path, last_accessed FROM recent_files ORDER BY last_accessed DESC"
        self.cursor.execute(query)
        recent_files = self.cursor.fetchall()

        # Populate the tree view
        for file_name, file_path, last_accessed in recent_files:
            date_str = last_accessed.strftime("%Y-%m-%d %H:%M")
            tree.insert("", "end", values=(file_name, date_str, file_path))

        # Add double-click functionality to open selected files
        def open_selected_file(event):
            selected_item = tree.selection()
            if selected_item:
                values = tree.item(selected_item, "values")
                file_path = values[2]  # Get the file path from the selected item
                if os.path.exists(file_path):
                    self.load_layout(file_path)
                    messagebox.showinfo("Recent File", f"Opened file: {os.path.basename(file_path)}")
                    recent_window.destroy()
                else:
                    messagebox.showerror("File Not Found", f"The file '{file_path}' no longer exists.")
                    self.update_database()  # Clean up invalid entries

        tree.bind("<Double-1>", open_selected_file)  # Open file on double-click



    def update_database(self):
        query = "SELECT id, file_path FROM recent_files"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        removed_files = 0

        for record_id, file_path in records:
            if not os.path.exists(file_path):
                # Delete the record for the missing file
                delete_query = "DELETE FROM recent_files WHERE id = %s"
                self.cursor.execute(delete_query, (record_id,))
                removed_files += 1

        if removed_files > 0:
            self.db.commit()
            messagebox.showinfo("Cleanup Completed", f"{removed_files} missing files were removed from the database.")
        else:
            messagebox.showinfo("Cleanup Completed", "No missing files found.")

    def serialize_widget(self, widget):
        """Serializes widget state for undo/redo and saving layouts."""
        if widget not in self.widget_ids:
            return None  # Skip if widget is no longer valid

        self.widget_info = {
            "type": type(widget).__name__,
            "text": widget.cget("text") if "text" in widget.keys() else "",
            "bg": widget.cget("bg") if "bg" in widget.keys() else "",
            "fg": widget.cget("fg") if "fg" in widget.keys() else "",
            "coords": self.canvas.coords(self.widget_ids[widget]),
            "size": (widget.winfo_width(), widget.winfo_height()),
        }

        # Include image path for image widgets
        if isinstance(widget, tk.Label) and hasattr(widget, "image"):
            self.widget_info["image_path"] = widget.image_path

        return self.widget_info


    def add_image_widget(self):
        # Open file dialog to select an image
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            # Load the image using Pillow
            original_image = Image.open(file_path)
            resized_image = original_image.resize((200, 200))  # Initial size

            # Convert the image to a PhotoImage
            image_tk = ImageTk.PhotoImage(resized_image)

            # Create a Label widget with the image
            image_label = tk.Label(self.canvas, image=image_tk, bg="white")
            image_label.image = image_tk  # Prevent garbage collection
            image_label.image_path = file_path  # Save the file path for serialization
            image_label.original_image = original_image  # Keep the original image for resizing later

            # Place the image widget on the canvas
            widget_id = self.canvas.create_window(100, 100, window=image_label, anchor="nw")

            # Store image widget details
            self.widgets.append(image_label)
            self.widget_ids[image_label] = widget_id

            # Bind events for drag and resize
            self.bind_widget_events(image_label)

            # Record state for undo/redo
            self.record_action("add", widget=image_label)

    def save_layout(self, event=None):
        layout_data = {
            "widgets": []
        }
        for widget in self.widgets:
            widget_info = {
                "type": type(widget).__name__,
                "text": widget.cget("text") if "text" in widget.keys() else "",
                "bg": widget.cget("bg") if "bg" in widget.keys() else "",
                "fg": widget.cget("fg") if "fg" in widget.keys() else "",
                "coords": self.canvas.coords(self.widget_ids[widget]),
                "size": (widget.winfo_width(), widget.winfo_height())
            }
            layout_data["widgets"].append(widget_info)

        # Save dialog
        file_path = filedialog.asksaveasfilename(defaultextension=".kpfile", filetypes=[("KP Files", "*.kpfile")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(layout_data, file)
            self.update_recent_files(os.path.basename(file_path), file_path)
            self.update_database()
            messagebox.showinfo("Save Layout", "Layout saved successfully.")


    def load_layout(self, file_path=None):
        if not file_path:
            # Open load dialog if no file path is provided
            file_path = filedialog.askopenfilename(filetypes=[("KP Files", "*.kpfile")])
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    layout_data = json.load(file)
                
                self.clear_all_widgets()  # Clear current widgets
                for widget_info in layout_data["widgets"]:
                    self.add_loaded_widget(widget_info)

                messagebox.showinfo("Load Layout", f"Layout loaded successfully from '{os.path.basename(file_path)}'.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load layout: {e}")


    def add_loaded_widget(self, widget_info):
        widget = None
        widget_type = widget_info["type"]

        if widget_type == "Button":
            widget = tk.Button(self.canvas, text=widget_info["text"], bg=widget_info["bg"], fg=widget_info["fg"])
        elif widget_type == "Label":
            widget = tk.Label(self.canvas, text=widget_info["text"], bg=widget_info["bg"], fg=widget_info["fg"])
        elif widget_type == "Entry":
            widget = tk.Entry(self.canvas, bg=widget_info["bg"])
        elif widget_type == "Frame":
            widget = tk.Frame(self.canvas, bg=widget_info["bg"], width=widget_info["size"][0], height=widget_info["size"][1])
        elif widget_type == "Checkbutton":
            widget = tk.Checkbutton(self.canvas, text=widget_info["text"])
        elif widget_type == "Radiobutton":
            widget = tk.Radiobutton(self.canvas, text=widget_info["text"])
        elif widget_type == "Text":
            widget = tk.Text(self.canvas, width=20, height=2, bg=widget_info["bg"])

        if widget:
            # Place the widget on the canvas
            widget_id = self.canvas.create_window(
                widget_info["coords"][0], widget_info["coords"][1],
                window=widget, anchor="nw",
                width=widget_info["size"][0], height=widget_info["size"][1]
            )
            self.widgets.append(widget)
            self.widget_ids[widget] = widget_id

            # Re-bind widget events
            self.bind_widget_events(widget)

    def bind_widget_events(self, widget):
        widget.bind("<Button-1>", self.start_long_click)
        widget.bind("<Button-3>", self.widget_right_click)
        widget.bind("<ButtonPress-1>", self.start_drag)
        widget.bind("<B1-Motion>", self.do_drag)
        widget.bind("<ButtonRelease-1>", self.stop_drag)
        widget.bind("<Double-1>", self.rename_widget)

    def create_toolbar(self):
        self.toolbar_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.toolbar_frame.pack(fill="x")
        
        toggle_btn = tk.Button(self.toolbar_frame, text="Toggle Ribbon", command=self.toggle_toolbar)
        toggle_btn.pack(side="left", padx=5, pady=5)


        for widget_type in ["Button", "Label", "Entry", "Frame", "Checkbutton", "Radiobutton", "Text"]:
            tk.Button(self.toolbar_frame, text=widget_type, 
                      command=lambda t=widget_type: self.add_widget(t)).pack(side="left", padx=5, pady=5)
        
        image_button = tk.Button(self.toolbar_frame, text="Add Image", command=self.add_image_widget)
        image_button.pack(side="left", padx=5, pady=5)
        treeview_button = tk.Button(self.toolbar_frame, text="Add Treeview", command=self.add_treeview_widget)
        treeview_button.pack(side="left", padx=5, pady=5)

    def toggle_toolbar(self):
        if self.toolbar_visible:
            self.toolbar_frame.pack_forget()
        else:
            self.toolbar_frame.pack(fill="x")
        self.toolbar_visible = not self.toolbar_visible

    def clear_all_widgets(self,event=None):
        for widget in self.widgets:
            widget_id = self.widget_ids.pop(widget, None)
            if widget_id:
                self.canvas.delete(widget_id)
        self.widgets.clear()
        messagebox.showinfo("Clear All", "All widgets have been cleared.")

    def create_canvas(self):
        self.canvas = tk.Canvas(self.root, bg="white", width=800, height=500)
        self.canvas.pack(pady=10, padx=10)

        # Create right-click menu for the canvas
        self.canvas_menu = tk.Menu(self.root, tearoff=0)
        self.canvas_menu.add_command(label="Resize Canvas Area", command=self.open_resize_canvas_dialog)

        # Bind right-click event to show the menu
        self.canvas.bind("<Button-3>", self.show_canvas_menu)

    def show_canvas_menu(self, event):
        self.canvas_menu.post(event.x_root, event.y_root)

    def open_resize_canvas_dialog(self):
        resize_win = tk.Toplevel(self.root)
        resize_win.title("Resize Canvas Area")
        
        tk.Label(resize_win, text="Canvas Width:").grid(row=0, column=0, padx=5, pady=5)
        width_var = tk.IntVar(value=self.canvas.winfo_width())
        width_entry = tk.Entry(resize_win, textvariable=width_var)
        width_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(resize_win, text="Canvas Height:").grid(row=1, column=0, padx=5, pady=5)
        height_var = tk.IntVar(value=self.canvas.winfo_height())
        height_entry = tk.Entry(resize_win, textvariable=height_var)
        height_entry.grid(row=1, column=1, padx=5, pady=5)

        apply_btn = tk.Button(resize_win, text="Apply", command=lambda: self.resize_canvas(width_var.get(), height_var.get()))
        apply_btn.grid(row=2, column=0, columnspan=2, pady=10)

    def resize_canvas(self, width, height):
        self.canvas.config(width=width, height=height)

    def start_long_click(self, event):
        widget = event.widget

        # Cancel any previous double-click timer
        if self.double_click_timer:
            self.root.after_cancel(self.double_click_timer)
            self.double_click_timer = None
        
        # Start the long click timer
        self.long_click_timer = self.root.after(self.long_click_duration, lambda: self.edit_properties(widget))

    
    def on_canvas_click(self, event):
        # Deselect any selected widgets and cancel long click
        self.canvas.focus_set()
        if self.long_click_timer:
            self.root.after_cancel(self.long_click_timer)
            self.long_click_timer = None

    def add_widget(self, widget_type):
        widget = None

        if widget_type == "Button":
            widget = tk.Button(self.canvas, text="Button", bg="lightgray")
        elif widget_type == "Label":
            widget = tk.Label(self.canvas, text="Label", bg="lightgray")
        elif widget_type == "Entry":
            widget = tk.Entry(self.canvas, bg="lightgray")
        elif widget_type == "Frame":
            widget = tk.Frame(self.canvas, bg="lightgray", width=100, height=50)
        elif widget_type == "Checkbutton":
            widget = tk.Checkbutton(self.canvas, text="Check")
        elif widget_type == "Radiobutton":
            widget = tk.Radiobutton(self.canvas, text="Radio")
        elif widget_type == "Text":
            widget = tk.Text(self.canvas, width=20, height=2, bg="lightgray")
        elif widget_type == "Label" and "image_path" in self.widget_info:
            # Recreate image widget
            image = tk.PhotoImage(file=self.widget_info["image_path"])
            widget = tk.Label(self.canvas, image=image, bg=self.widget_info["bg"])
            widget.image = image
            widget.image_path = self.widget_info["image_path"]

        # Bind widget events
        widget.bind("<Button-1>", self.start_long_click)
        widget.bind("<Button-3>", self.widget_right_click)
        widget.bind("<ButtonPress-1>", self.start_drag)
        widget.bind("<B1-Motion>", self.do_drag)
        widget.bind("<ButtonRelease-1>", self.stop_drag)
        widget.bind("<Double-1>", self.rename_widget)

        # Place widget with initial dimensions, e.g., width=100, height=50 for example
        widget_id = self.canvas.create_window(100, 100, window=widget, anchor="nw", width=100, height=50)
        self.widgets.append(widget)
        self.widget_ids[widget] = widget_id

        # Add resize handles to the widget
        self.add_resize_handles(widget)
        self.record_action("add", widget=widget)


    def add_treeview_widget(self):
        """Add a new Treeview widget to the canvas."""
        treeview = ttk.Treeview(self.canvas, columns=('Column1', 'Column2', 'Column3'), show='headings', height=8)
        treeview.heading('Column1', text='Column1')
        treeview.column('Column1', width=200, anchor='w')
        treeview.heading('Column2', text='Column2')
        treeview.column('Column2', width=200, anchor='center')
        treeview.heading('Column3', text='Column3')
        treeview.column('Column3', width=200, anchor='e')

        # Place the Treeview on the canvas
        widget_id = self.canvas.create_window(100, 100, window=treeview, anchor="nw")
        self.widgets.append(treeview)
        self.widget_ids[treeview] = widget_id

        # Bind events for drag and resize
        self.bind_widget_events(treeview)

        # Add resize handles
        self.add_resize_handles(treeview)

    def bind_treeview_events(self, treeview):
        """Bind events for Treeview actions."""
        # Right-click context menu for Treeview
        menu_tree = tk.Menu(self.root, tearoff=0)
        menu_tree.add_command(label="Add Row", command=lambda: self.add_treeview_row(treeview))
        menu_tree.add_command(label="Add Column", command=lambda: self.add_treeview_column(treeview))
        menu_tree.add_command(label="Rename Column", command=lambda: self.rename_treeview_header(treeview))

        def show_menu(event):
            menu_tree.post(event.x_root, event.y_root)

        treeview.bind("<Button-3>", show_menu) 


    def rename_treeview_header(self, event, treeview):
        # Identify the column header clicked
        region = treeview.identify_region(event.x, event.y)
        if region == "heading":
            column = treeview.identify_column(event.x)

            # Prompt user for a new header name
            new_name = tk.simpledialog.askstring("Rename Header", f"Enter new name for {column}:")
            if new_name:
                treeview.heading(column, text=new_name)
    
    def add_treeview_row(self, treeview):
        # Prompt user for row data
        num_columns = len(treeview["columns"])
        row_data = []
        for i in range(num_columns):
            value = tk.simpledialog.askstring(f"Column {i + 1}", f"Enter value for Column {i + 1}:")
            row_data.append(value if value else "")

        # Insert the new row
        treeview.insert("", "end", values=row_data)

    def add_treeview_column(self, treeview):
        # Prompt user for the new column name
        column_name = tk.simpledialog.askstring("New Column", "Enter new column name:")
        if not column_name:
            return  # Exit if no column name is provided

        # Add the new column to the Treeview
        columns = list(treeview["columns"]) + [column_name]
        treeview["columns"] = columns
        treeview.heading(column_name, text=column_name)
        treeview.column(column_name, width=100, anchor="center")
    def add_resize_handles(self, widget):
        # Add resize handles (top-left, bottom-right) to the widget
        directions = ['top_left', 'bottom_right']
        for direction in directions:
            handle = tk.Frame(self.canvas, width=8, height=8, bg="blue", cursor="size_all")
            handle.bind("<Button-1>", lambda e, d=direction: self.start_resize(e, widget, d))
            handle.bind("<B1-Motion>", lambda e, d=direction: self.do_resize(e, widget, d))
            handle.bind("<ButtonRelease-1>", self.stop_resize)

            # Position the handle
            handle_id = self.canvas.create_window(0, 0, window=handle, tags=(f"{widget}_{direction}",))
            self.position_handles(widget)

    def position_handles(self, widget):
        if widget not in self.widget_ids:
            return  # Widget no longer exists

        x, y = self.canvas.coords(self.widget_ids[widget])
        w, h = widget.winfo_width(), widget.winfo_height()

        handle_positions = {
            'top': (x + w // 2, y),
            'bottom': (x + w // 2, y + h),
            'left': (x, y + h // 2),
            'right': (x + w, y + h // 2),
            'top_left': (x, y),
            'top_right': (x + w, y),
            'bottom_left': (x, y + h),
            'bottom_right': (x + w, y + h),
        }

        for direction, position in handle_positions.items():
            tag = f"{widget}_{direction}"
            if self.canvas.find_withtag(tag):  # Ensure the handle exists
                self.canvas.coords(tag, position)


    def get_cursor(self, direction):
        cursors = {
            'top': 'top_side', 'bottom': 'bottom_side',
            'left': 'left_side', 'right': 'right_side',
            'top_left': 'top_left_corner', 'top_right': 'top_right_corner',
            'bottom_left': 'bottom_left_corner', 'bottom_right': 'bottom_right_corner',
        }
        return cursors[direction]

    def start_drag(self, event):
        # Store initial click position for drag
        self.dragging_widget = event.widget
        self.offset_x = event.x
        self.offset_y = event.y

        # Cancel long click if dragging starts
        if self.long_click_timer:
            self.root.after_cancel(self.long_click_timer)
            self.long_click_timer = None

    def do_drag(self, event):
        if self.dragging_widget and not self.resizing:
            widget_id = self.widget_ids.get(self.dragging_widget)
            if widget_id:  # Ensure widget_id is valid
                previous_coords = self.canvas.coords(widget_id)
                x = previous_coords[0] - self.offset_x + event.x
                y = previous_coords[1] - self.offset_y + event.y
                self.canvas.coords(widget_id, x, y)
                self.record_action("move", widget=self.dragging_widget, data={
                    "previous_coords": previous_coords,
                    "new_coords": [x, y]
                })
                self.position_handles(self.dragging_widget)



    def stop_drag(self, event):
        self.dragging_widget = None

    def start_resize(self, event, widget, direction):
        self.resizing = True
        self.resize_direction = direction
        self.dragging_widget = widget
        self.offset_x = event.x
        self.offset_y = event.y


    def do_resize(self, event, widget, direction):
        if self.resizing:
            previous_width = widget.winfo_width()
            previous_height = widget.winfo_height()
            new_width = max(previous_width + (event.x - self.offset_x), 1)
            new_height = max(previous_height + (event.y - self.offset_y), 1)
            widget.config(width=new_width, height=new_height)
            self.record_action("resize", widget=widget, data={
                "previous_width": previous_width,
                "previous_height": previous_height,
                "new_width": new_width,
                "new_height": new_height,
            })
            self.position_handles(widget)

    def stop_resize(self, event):
        self.resizing = False
        self.resize_direction = None
        self.dragging_widget = None

    def widget_right_click(self, event):
        widget = event.widget
        # Initialize function states for the widget if not already done
        if widget not in self.function_states:
            self.function_states[widget] = {
                "open_file": tk.BooleanVar(value=False),
                "save_file": tk.BooleanVar(value=False),
                "get_text": tk.BooleanVar(value=False),
            }

        widget_menu = tk.Menu(self.root, tearoff=0)
        widget_menu.add_command(label="Rename", command=lambda: self.rename_widget(widget))
        widget_menu.add_command(label="Copy", command=lambda: self.copy_widget(widget))
        widget_menu.add_command(label="Delete", command=lambda: self.delete_widget(widget))
        widget_menu.add_command(label="Properties", command=lambda: self.edit_properties(widget))

        # Add Function submenu
        add_function_menu = tk.Menu(widget_menu, tearoff=0)
        add_function_menu.add_checkbutton(
            label="Open File",
            variable=self.function_states[widget]["open_file"],
            command=lambda: self.toggle_function(widget, "open_file"),
        )
        add_function_menu.add_checkbutton(
            label="Save File",
            variable=self.function_states[widget]["save_file"],
            command=lambda: self.toggle_function(widget, "save_file"),
        )
        add_function_menu.add_checkbutton(
            label="Get Text",
            variable=self.function_states[widget]["get_text"],
            command=lambda: self.toggle_function(widget, "get_text"),
        )
        # Add custom function option
        widget_menu.add_command(label="Add Custom Function", command=lambda: self.add_custom_function(widget))

        # Add Function submenu to the main context menu
        widget_menu.add_cascade(label="Add Function", menu=add_function_menu)

        # Add Manage Functions option
        widget_menu.add_command(label="Manage Functions", command=lambda: self.manage_functions(widget))
        # Post the menu at the position of the mouse click
        widget_menu.post(event.x_root, event.y_root)

    # Function to toggle applied functions
    def toggle_function(self, widget, function_name):
        if function_name not in self.function_states[widget]:
            self.function_states[widget][function_name] = tk.BooleanVar(value=False)

        is_selected = self.function_states[widget][function_name].get()
        if is_selected:  # If function is being applied
            if function_name == "open_file":
                self.add_open_file(widget)
            elif function_name == "save_file":
                self.add_save_file(widget)
            elif function_name == "get_text":
                self.add_get_text(widget)
        else:  # If function is being removed
            if widget in self.widget_functions:
                del self.widget_functions[widget]
            messagebox.showinfo("Function Removed", f"{function_name.replace('_', ' ').capitalize()} function removed from widget.")
    

    def restore_state(self, state):
        """Restores the canvas state."""
        self.clear_all_widgets()
        for widget_info in state["widgets"]:
            self.add_loaded_widget(widget_info)

    def record_action(self, action_type, widget=None, data=None):
        """Records an action for Undo/Redo."""
        action = {
            "type": action_type,
            "widget": widget,
            "data": data,
        }
        self.undo_stack.append(action)
        self.redo_stack.clear()  # Clear redo stack whenever a new action is recorded.

    def undo_action(self, event=None):
        if not self.undo_stack:
            return
        action = self.undo_stack.pop()
        self.redo_stack.append(action)

        # Undo based on action type
        if action["type"] == "add":
            self.delete_widget(action["widget"])
        elif action["type"] == "delete":
            self.add_loaded_widget(action["data"])
        elif action["type"] == "move":
            widget_id = self.widget_ids[action["widget"]]
            self.canvas.coords(widget_id, *action["data"]["previous_coords"])
        elif action["type"] == "resize":
            action["widget"].config(width=action["data"]["previous_width"], height=action["data"]["previous_height"])

    def redo_action(self, event=None):
        if not self.redo_stack:
            return
        action = self.redo_stack.pop()
        self.undo_stack.append(action)

        if action["type"] == "delete":
            # Recreate the deleted widget
            self.add_loaded_widget(action["data"])


        # Redo based on action type
        if action["type"] == "add":
            self.add_loaded_widget(action["data"])
        elif action["type"] == "delete":
            self.delete_widget(action["widget"])
        elif action["type"] == "move":
            widget_id = self.widget_ids[action["widget"]]
            self.canvas.coords(widget_id, *action["data"]["new_coords"])
        elif action["type"] == "resize":
            action["widget"].config(width=action["data"]["new_width"], height=action["data"]["new_height"])

#add functions----------
        
    def add_custom_function(self, widget):
        # Create a top-level window to display the multi-line text box
        custom_function_window = tk.Toplevel(self.root)
        custom_function_window.title("Enter Custom Function Code")

        text_label1 = tk.Label(custom_function_window, width=100, height=3,text="For creating variable, just type any name in below, name box, and write variable's value in this box")
        text_label1.pack(padx=2,pady=2)
        text_box = tk.Text(custom_function_window, width=100, height=10)
        text_box.pack(padx=10, pady=10)
        text_label2 = tk.Label(custom_function_window, width=10, height=3,text="Name, if it have any parameter, like my_num(a,b,....)")
        text_label2.pack(padx=2,pady=2)
        name_box = tk.Text(custom_function_window, width=8, height=5)
        name_box.pack(padx=10, pady=20)

        def save_function():
            custom_function_code = text_box.get("1.0", "end-1c")  # Get the code entered in the text box

            if custom_function_code.strip():
                # Store the custom function code in the widget's function dictionary
                if widget not in self.widget_functions:
                    self.widget_functions[widget] = {}

                # You could allow the user to name their custom function
                custom_function_name = name_box.get("1.0", "end-1c")
                self.widget_functions[widget][custom_function_name] = custom_function_code

                messagebox.showinfo("Function Added", f"Custom function added to widget.")
                custom_function_window.destroy()
            else:
                messagebox.showwarning("Invalid Input", "Please enter some code for the function.")

        # Add Save button to store the function
        save_button = tk.Button(custom_function_window, text="Save Function", command=save_function)
        save_button.pack(pady=5, padx=5)

    def manage_functions(self, widget):
        if widget not in self.widget_functions or not self.widget_functions[widget]:
            messagebox.showinfo("Manage Functions", "No functions are currently applied to this widget.")
            return

        # Create a small dialog window
        manage_win = tk.Toplevel(self.root)
        manage_win.title("Manage Functions")
        manage_win.geometry("300x200")

        tk.Label(manage_win, text="Right-click a function for options", font=("Arial", 10)).pack(pady=5)

        # Display the functions in a Listbox
        function_list = tk.Listbox(manage_win, height=8, width=35)
        for func_name in self.widget_functions[widget]:
            function_list.insert(tk.END, func_name)
        function_list.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        # Create the context menu
        function_menu = tk.Menu(manage_win, tearoff=0)
        function_menu.add_command(label="Edit Function", command=lambda: edit_function())
        function_menu.add_command(label="Remove Function", command=lambda: remove_function())

        def show_context_menu(event):
            selected = function_list.curselection()
            if not selected:
                return  # Don't show the menu if nothing is selected
            function_menu.post(event.x_root, event.y_root)

        function_list.bind("<Button-3>", show_context_menu)  # Right-click to show the menu

        def edit_function():
            selected = function_list.curselection()
            if not selected:
                messagebox.showwarning("Edit Function", "Please select a function to edit.")
                return

            func_name = function_list.get(selected[0])
            func_code = self.widget_functions[widget][func_name]

            # Open an inline editor for the function
            edit_win = tk.Toplevel(manage_win)
            edit_win.title(f"Edit Function: {func_name}")
            edit_win.geometry("500x400")

            tk.Label(edit_win, text="Function Code:", font=("Arial", 12)).pack(pady=10)
            code_text = tk.Text(edit_win, wrap="word", height=10, width=50)
            code_text.insert("1.0", func_code)
            code_text.pack(pady=10)

            def save_changes():
                updated_code = code_text.get("1.0", "end-1c")
                if updated_code.strip():
                    self.widget_functions[widget][func_name] = updated_code
                    messagebox.showinfo("Edit Function", f"Function '{func_name}' updated successfully.")
                    edit_win.destroy()
                else:
                    messagebox.showwarning("Edit Function", "Function code cannot be empty.")

            tk.Button(edit_win, text="Save Changes", command=save_changes).pack(pady=10)

        def remove_function():
            selected = function_list.curselection()
            if not selected:
                messagebox.showwarning("Remove Function", "Please select a function to remove.")
                return

            func_name = function_list.get(selected[0])
            del self.widget_functions[widget][func_name]
            function_list.delete(selected[0])
            messagebox.showinfo("Remove Function", f"Function '{func_name}' removed successfully.")

# pre defined functoins
    def add_open_file(self, widget):
        if widget not in self.widget_functions:
            self.widget_functions[widget] = {}
        
        self.widget_functions[widget]["open_file"] = (
            "def open_file():\n"
            "    filepath = filedialog.askopenfilename(initialdir='/', title='Open a file')\n"
            "    return filepath\n"
        )
        messagebox.showinfo("Function Added", "Open File function added to widget.")

    # Function to add "Save File"
    def add_save_file(self, widget):
        if widget not in self.widget_functions:
            self.widget_functions[widget] = {}
        
        self.widget_functions[widget]["save_file"] = (
            "def save_file():\n"
            "    filepath = filedialog.asksaveasfile(initialdir='/', title='Save a file')\n"
            "    return filepath\n"
        )
        messagebox.showinfo("Function Added", "Save File function added to widget.")

    # Function to add "Get Text"
    def add_get_text(self, widget):
        if widget not in self.widget_functions:
            self.widget_functions[widget] = {}

        widget_name = f"{type(widget).__name__.lower()}{len(self.widgets)}"
        if isinstance(widget, tk.Entry):
            self.widget_functions[widget]["get_text"] = (
                f"def get_text_{widget_name}():\n"
                f"    return {widget_name}.get()\n"
            )
        elif isinstance(widget, tk.Button):
            self.widget_functions[widget]["get_text"] = (
                f"def get_text_{widget_name}():\n"
                f"    return '{widget['text']}'\n"
            )
        messagebox.showinfo("Function Added", "Get Text function added to widget.")



    def copy_widget(self, widget):
        # Copies widget properties to a new instance
        widget_type = type(widget).__name__
        new_widget = None

        # Re-create widget based on its type
        if widget_type == "Button":
            new_widget = tk.Button(self.canvas, text=widget.cget("text"), bg=widget.cget("bg"), fg=widget.cget("fg"))
        elif widget_type == "Label":
            new_widget = tk.Label(self.canvas, text=widget.cget("text"), bg=widget.cget("bg"), fg=widget.cget("fg"))
        elif widget_type == "Entry":
            new_widget = tk.Entry(self.canvas, bg=widget.cget("bg"))
        elif widget_type == "Frame":
            new_widget = tk.Frame(self.canvas, bg=widget.cget("bg"), width=widget.winfo_width(), height=widget.winfo_height())
        elif widget_type == "Checkbutton":
            new_widget = tk.Checkbutton(self.canvas, text=widget.cget("text"))
        elif widget_type == "Radiobutton":
            new_widget = tk.Radiobutton(self.canvas, text=widget.cget("text"))
        elif widget_type == "Text":
            new_widget = tk.Text(self.canvas, width=20, height=2, bg=widget.cget("bg"))

        if new_widget:
            # Copy basic properties
            for option in widget.keys():
                try:
                    new_widget.config({option: widget.cget(option)})
                except tk.TclError:
                    continue

            # Place widget on canvas with an offset
            x, y = self.canvas.coords(self.widget_ids[widget])
            widget_id = self.canvas.create_window(x + 10, y + 10, window=new_widget, anchor="nw", width=widget.winfo_width(), height=widget.winfo_height())
            self.widgets.append(new_widget)
            self.widget_ids[new_widget] = widget_id

            # Re-bind the necessary events for the new widget
            new_widget.bind("<Button-1>", self.start_long_click)
            new_widget.bind("<Button-3>", lambda e: self.widget_right_click(e))
            new_widget.bind("<ButtonPress-1>", self.start_drag)
            new_widget.bind("<B1-Motion>", self.do_drag)
            new_widget.bind("<ButtonRelease-1>", self.stop_drag)
            new_widget.bind("<Double-1>", lambda e: self.rename_widget(e))

            # Add resize handles to the new widget
            self.add_resize_handles(new_widget)

    def rename_widget(self, event):
        if self.long_click_timer:
            self.root.after_cancel(self.long_click_timer)
            self.long_click_timer = None
        
        widget = event.widget
        rename_win = tk.Toplevel(self.root)
        rename_win.title("Rename Widget")

        tk.Label(rename_win, text="New Name:").grid(row=0, column=0)
        name_var = tk.StringVar(value=widget.cget("text") if hasattr(widget, "cget") else "")
        name_entry = tk.Entry(rename_win, textvariable=name_var)
        name_entry.grid(row=0, column=1)

        tk.Button(rename_win, text="Rename", command=lambda: self.apply_name(widget, name_var.get())).grid(row=1, column=0, columnspan=2)

        def apply_name():
            new_name = name_var.get()
            widget.config(text=new_name)
            rename_win.destroy()

        tk.Button(rename_win, text="Apply", command=apply_name).grid(row=1, column=0, columnspan=2)
    
    def edit_properties(self, widget):
        prop_win = tk.Toplevel(self.root)
        prop_win.title("Edit Properties")

        # Padding
        tk.Label(prop_win, text="Padding:").grid(row=0, column=0)
        padding_var = tk.StringVar(value=str(widget.cget("padx") if "padx" in widget.keys() else "0"))
        padding_entry = tk.Entry(prop_win, textvariable=padding_var)
        padding_entry.grid(row=0, column=1)

        # Width
        tk.Label(prop_win, text="Width:").grid(row=1, column=0)
        width_var = tk.StringVar(value=str(widget.winfo_width()))
        width_entry = tk.Entry(prop_win, textvariable=width_var)
        width_entry.grid(row=1, column=1)

        # Height
        tk.Label(prop_win, text="Height:").grid(row=2, column=0)
        height_var = tk.StringVar(value=str(widget.winfo_height()))
        height_entry = tk.Entry(prop_win, textvariable=height_var)
        height_entry.grid(row=2, column=1)

        # Background Color
        tk.Label(prop_win, text="Background Color:").grid(row=3, column=0)
        bg_color_var = tk.StringVar(value=widget.cget("bg"))
        bg_color_entry = tk.Entry(prop_win, textvariable=bg_color_var)
        bg_color_entry.grid(row=3, column=1)

        fg_color_var = None
        if "fg" in widget.keys():
            tk.Label(prop_win, text="Foreground Color:").grid(row=4, column=0)
            fg_color_var = tk.StringVar(value=widget.cget("fg"))
            fg_color_entry = tk.Entry(prop_win, textvariable=fg_color_var)
            fg_color_entry.grid(row=4, column=1)

        # Font Size and Font Style
        font_size_var = tk.IntVar(value=12)  # Default font size
        font_style_var = tk.StringVar(value="normal")  # Default font style

        if isinstance(widget, (tk.Label, tk.Button, tk.Checkbutton, tk.Radiobutton, tk.Entry)):
            tk.Label(prop_win, text="Font Size:").grid(row=5, column=0)
            font_size_entry = tk.Entry(prop_win, textvariable=font_size_var)
            font_size_entry.grid(row=5, column=1)

            tk.Label(prop_win, text="Font Style:").grid(row=6, column=0)
            font_style_dropdown = ttk.Combobox(prop_win, values=["normal", "bold", "italic"], textvariable=font_style_var)
            font_style_dropdown.grid(row=6, column=1)

        # Apply button
        tk.Button(prop_win, text="Apply", command=lambda: self.apply_properties(
            widget, prop_win, padding_var, width_var, height_var, bg_color_var, fg_color_var, font_size_var, font_style_var
        )).grid(row=7, column=1)

    def apply_properties(self, widget, prop_win, padding_var, width_var, height_var, bg_color_var, fg_color_var, font_size_var, font_style_var):
        try:
            # Padding
            if "padx" in widget.keys():
                widget.config(padx=int(padding_var.get()), pady=int(padding_var.get()))

            # New width and height entered by the user
            new_width = int(width_var.get())
            new_height = int(height_var.get())

            # Apply font and colors to the widget
            widget.config(bg=bg_color_var.get())
            if "fg" in widget.keys():
                widget.config(fg=fg_color_var.get())
            if isinstance(widget, (tk.Label, tk.Button, tk.Checkbutton, tk.Radiobutton, tk.Entry)):
                widget.config(font=(None, font_size_var.get(), font_style_var.get()))
            
            # Apply image size/scalingS
            if isinstance(widget, tk.Label) and hasattr(widget, "original_image"):
                resized_image = widget.original_image.resize((new_width, new_height), Image.LANCZOS)  # Use LANCZOS instead of ANTIALIAS
                widget.image = ImageTk.PhotoImage(resized_image)
                widget.config(image=widget.image)
            # Store the custom width and height
            widget.custom_width = new_width
            widget.custom_height = new_height

            # Update the widget on the canvas with new dimensions
            widget_id = self.widget_ids[widget]
            x, y = self.canvas.coords(widget_id)
            self.canvas.coords(widget_id, x, y)  # Keeps the widget at the same position
            self.canvas.itemconfigure(widget_id, width=new_width, height=new_height)  # Set exact pixel width and height

            # Re-position handles after resizing
            self.position_handles(widget)
            self.canvas.update_idletasks()

            # Close the dialog after applying properties
            prop_win.destroy()

        except tk.TclError as e:
            messagebox.showerror("Error", f"Failed to apply properties: {e}")


    def delete_widget(self, widget):
        if widget not in self.widget_ids:
            return  # Widget already deleted or invalid

        # Serialize widget data before deletion
        widget_data = self.serialize_widget(widget)
        self.record_action("delete", data=widget_data)

        # Remove widget from canvas and internal tracking
        widget_id = self.widget_ids.pop(widget)
        self.canvas.delete(widget_id)
        self.widgets.remove(widget)


    def generate_code(self, event=None):
        # Initialize the script with imports and root setup
        code = (
            "import tkinter as tk\n"
            "from tkinter import filedialog\n"
            "from tkinter import ttk\n"
            "from PIL import Image, ImageTk\n\n"
            "root = tk.Tk()\n"
            f"root.geometry('{self.canvas.winfo_width()}x{self.canvas.winfo_height()}')\n"
            "root.title('your_app_name')\n\n"
        )
        # Track functions already added to avoid duplicates
        added_functions = set()
        widget_declarations = ""  # Collect widget declarations here
        widget_placements = ""  # Collect widget placements here
        used_names = set()

        # Process each widget
        for widget in self.widgets:
            widget_type = type(widget).__name__
            widget_name = self.generate_unique_name(widget_type.lower(), used_names)
            widget_code = f"{widget_name} = tk.{widget_type}(root"

            # Get widget coordinates
            coords = self.canvas.coords(self.widget_ids[widget]) if widget in self.widget_ids else (0, 0)
            x, y = int(coords[0]), int(coords[1])

            if isinstance(widget, ttk.Treeview):
                # Generate Treeview code
                columns = widget["columns"]
                widget_declarations += (
                    f"# Create a Treeview widget\n"
                    f"{widget_name} = ttk.Treeview(root, columns={columns}, show='headings', height=8)\n"
                )
                for col in columns:
                    col_heading = widget.heading(col)["text"]
                    col_anchor = widget.column(col).get("anchor", "center")
                    col_width = widget.column(col).get("width", 100)
                    widget_declarations += (
                        f"{widget_name}.heading('{col}', text='{col_heading}')\n"
                        f"{widget_name}.column('{col}', width={col_width}, anchor='{col_anchor}')\n"
                    )
                widget_declarations += f"{widget_name}.pack(fill='both', expand=True, padx=10, pady=10)\n\n"
            #for image
            if isinstance(widget, tk.Label) and hasattr(widget, "image"):
                # Handle image labels
                image_path = widget.image_path.replace("\\", "\\\\")  # Escape backslashes
                widget_declarations += (
                    f"original_image = Image.open(r'{image_path}')\n"
                    f"resized_image = original_image.resize(({widget.winfo_width()}, {widget.winfo_height()}), Image.LANCZOS)\n"
                    f"{widget_name}_image = ImageTk.PhotoImage(resized_image)\n"
                    f"{widget_name} = tk.Label(root, image={widget_name}_image, bg='{widget.cget('bg')}')\n"
                )
            else:
                # Handle other widget types
                widget_declarations += f"{widget_name} = tk.{widget_type}(root"
                if widget_type in ["Button", "Label"]:
                    widget_declarations += f", text='{widget.cget('text')}', bg='{widget.cget('bg')}', fg='{widget.cget('fg')}'"
                if widget_type == "Entry":
                    widget_declarations += f", bg='{widget.cget('bg')}', width={widget.cget('width')}"
                if widget_type == "Frame":
                    widget_declarations += f", bg='{widget.cget('bg')}'"
                widget_declarations += ")\n"

            # Add command for predefined or custom functions
            if widget in self.widget_functions and isinstance(self.widget_functions[widget], dict):
                
                for function_name in self.widget_functions[widget]:
                    if function_name in ["open_file", "save_file", "get_text"]:
                        widget_code = widget_code.replace(')', f", command={function_name})")
                
                
                for function_name, function_code in self.widget_functions[widget].items():
                        
                    if "get_text" in function_name:  # Handle unique get_text
                        unique_function_name = f"get_text_{widget_name}"
                        widget_code += f", command={unique_function_name}"

                        # Generate the unique function definition if not already added
                        unique_function_code = f"def {unique_function_name}():\n    return '{widget['text']}'"
                        if unique_function_name not in added_functions:
                            code += unique_function_code + "\n\n"
                            added_functions.add(unique_function_name)
                    else:  # Custom functions
                        widget_code += f", command={function_name}"

                        if function_name not in added_functions:
                            code += function_code + "\n\n"
                            added_functions.add(function_name)

                widget_code += ")\n"  # Close widget declaration
                widget_declarations += widget_code
            x, y = self.canvas.coords(self.widget_ids[widget])
            widget_placements += f"{widget_name}.place(x={int(x)}, y={int(y)},width={widget.winfo_width()}, height={widget.winfo_height()})\n\n"
    
        # Combine everything into final code
        code += widget_declarations  
        code += widget_placements  
        code += "root.mainloop()"

        self.show_code_window(code)
    
    def generate_unique_name(self, base_name, used_names):
        """Generate a unique name for widgets to avoid overwrites."""
        name = base_name
        counter = 0
        while name in used_names:
            counter += 1
            name = f"{base_name}{counter}"
        used_names.add(name)
        return name

    def show_code_window(self, code):
        code_win = tk.Toplevel(self.root)
        code_win.title("Generated Code")

        code_text = tk.Text(code_win, wrap="word")
        code_text.insert("1.0", code)
        code_text.pack(expand=True, fill="both")

        copy_btn = tk.Button(code_win, text="Copy Code", command=lambda: self.copy_code_to_clipboard(code))
        copy_btn.pack()

# will def clipboard_clear() and clipboard_append() in next version........
    def copy_code_to_clipboard(self, code):
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        messagebox.showinfo("Copied", "Code copied to clipboard!")

    def save_generated_code(self):
        # Generate the code using the existing generate_code logic
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        code = (
            "import tkinter as tk\n"
            "from tkinter import filedialog\n"
            "from PIL import Image, ImageTk\n\n"
            f"root = tk.Tk()\nroot.geometry('{width}x{height}')\nroot.title('your_app_name')\n\n"
        )

        widget_declarations = ""
        widget_placements = ""
        used_names = set()

        for widget in self.widgets:
            widget_type = type(widget).__name__
            widget_name = self.generate_unique_name(widget_type.lower(), used_names)

            if isinstance(widget, tk.Label) and hasattr(widget, "image"):
                image_path = widget.image_path.replace("\\", "\\\\")
                widget_declarations += (
                    f"original_image = Image.open(r'{image_path}')\n"
                    f"resized_image = original_image.resize(({widget.winfo_width()}, {widget.winfo_height()}), Image.LANCZOS)\n"
                    f"{widget_name}_image = ImageTk.PhotoImage(resized_image)\n"
                    f"{widget_name} = tk.Label(root, image={widget_name}_image, bg='{widget.cget('bg')}')\n"
                )
            else:
                widget_code = f"{widget_name} = tk.{widget_type}(root"
                if widget_type in ["Button", "Label"]:
                    widget_code += f", text='{widget.cget('text')}', bg='{widget.cget('bg')}', fg='{widget.cget('fg')}'"
                if widget_type == "Entry":
                    widget_code += f", bg='{widget.cget('bg')}', width={widget.cget('width')}"
                if widget_type == "Frame":
                    widget_code += f", bg='{widget.cget('bg')}'"
                widget_code += ")\n"
                widget_declarations += widget_code

            x, y = self.canvas.coords(self.widget_ids[widget])
            widget_placements += f"{widget_name}.place(x={int(x)}, y={int(y)}, width={widget.winfo_width()}, height={widget.winfo_height()})\n"

        code += widget_declarations
        code += widget_placements
        code += "\nroot.mainloop()"

        # Ask the user to specify the file name
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py")],
            title="Save Generated Code"
        )

        # Save the code to the file if a path is provided
        if file_path:
            try:
                with open(file_path, "w") as file:
                    file.write(code)
                messagebox.showinfo("Success", f"Generated code saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TkinterAppDesigner(root)
    controller=HandMouseController()
    controller.start()
    root.mainloop()