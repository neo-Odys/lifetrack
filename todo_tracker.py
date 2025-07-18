import tkinter as tk
from tkinter import messagebox, simpledialog
from database import (
    add_task, get_tasks_by_date, update_task_status, delete_task, update_task_text
)

class TodoTracker:
    def __init__(self, parent, current_date, update_callback=None):
        self.parent = parent
        self.current_date = current_date
        self.update_callback = update_callback
        self.todo_widgets = []
        self.create_widgets()
        self.load_todos()

    def create_widgets(self):
        # Main frame for todos
        self.main_frame = tk.Frame(self.parent, bg='#2C2C2C')
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header with add button
        header_frame = tk.Frame(self.main_frame, bg='#2C2C2C')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text="Todo List", font=('JetBrains Mono', 12, 'bold'),
                bg='#2C2C2C', fg='white').pack(side='left')
        
        add_btn = tk.Button(header_frame, text="+", command=self.add_todo,
                          font=('JetBrains Mono', 12, 'bold'), bg='#404040', fg='white',
                          activebackground='#505050', border=0, padx=10)
        add_btn.pack(side='right')
        
        # Scrollable todo list
        self.todo_frame = tk.Frame(self.main_frame, bg='#2C2C2C')
        self.todo_frame.pack(fill='both', expand=True)

    def load_todos(self):
        """Load todos for the current date"""
        # Clear existing todo widgets
        for widget_group in self.todo_widgets:
            for widget in widget_group:
                widget.destroy()
        self.todo_widgets.clear()
        
        # Load todos for current date
        current_date = self.current_date.strftime("%d-%m-%Y")
        todos = get_tasks_by_date(current_date)
        
        for todo in todos:
            todo_id, date, task_text, completed = todo
            self._create_todo_widget(todo_id, task_text, completed)

    def _create_todo_widget(self, todo_id, task_text, completed):
        """Create a single todo widget"""
        todo_row = tk.Frame(self.todo_frame, bg='#2C2C2C')
        todo_row.pack(fill='x', pady=2)
        
        # Checkbox
        var = tk.BooleanVar(value=completed)
        checkbox = tk.Checkbutton(todo_row, variable=var, 
                                bg='#2C2C2C', fg='white', selectcolor='#404040',
                                activebackground='#2C2C2C', activeforeground='white',
                                command=lambda: self.toggle_todo(todo_id, var.get()))
        checkbox.pack(side='left')
        
        # Task text (clickable to edit)
        text_color = '#888888' if completed else 'white'
        task_label = tk.Label(todo_row, text=task_text, 
                             font=('JetBrains Mono', 10), bg='#2C2C2C', fg=text_color,
                             cursor='hand2', wraplength=200, justify='left')
        task_label.pack(side='left', fill='x', expand=True, padx=(5, 0))
        task_label.bind("<Button-1>", lambda e: self.edit_todo(todo_id, task_text))
        
        # Delete button
        delete_btn = tk.Button(todo_row, text="×", command=lambda: self.delete_todo(todo_id),
                              font=('JetBrains Mono', 10, 'bold'), bg='#660000', fg='white',
                              activebackground='#880000', border=0, padx=5)
        delete_btn.pack(side='right')
        
        self.todo_widgets.append([todo_row, checkbox, task_label, delete_btn])

    def add_todo(self):
        """Add a new todo"""
        task_text = simpledialog.askstring("Add Task", "Enter task:")
        if task_text and task_text.strip():
            current_date = self.current_date.strftime("%d-%m-%Y")
            add_task(current_date, task_text.strip(), False)
            self.load_todos()
            
            if self.update_callback:
                self.update_callback()

    def edit_todo(self, todo_id, current_text):
        """Edit an existing todo"""
        new_text = simpledialog.askstring("Edit Task", "Edit task:", initialvalue=current_text)
        if new_text and new_text.strip():
            update_task_text(todo_id, new_text.strip())
            self.load_todos()
            
            if self.update_callback:
                self.update_callback()

    def delete_todo(self, todo_id):
        """Delete a todo"""
        if messagebox.askyesno("Delete Task", "Are you sure you want to delete this task?"):
            delete_task(todo_id)
            self.load_todos()
            
            if self.update_callback:
                self.update_callback()

    def toggle_todo(self, todo_id, completed):
        """Toggle todo completion status"""
        update_task_status(todo_id, completed)
        self.load_todos()
        
        if self.update_callback:
            self.update_callback()

    def update_date(self, new_date):
        """Update current date and reload todos"""
        self.current_date = new_date
        self.load_todos()