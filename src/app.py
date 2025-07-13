import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime, timedelta
from database import (
    add_activity, check_activity, create_habit_table, 
    add_habit_status, check_habit_status, get_habit_names,
    add_task, get_tasks_by_date, update_task_status, delete_task, update_task_text
)

class ActivityTracker:
    def __init__(self, master):
        self.master = master
        self._setup_window()
        
        self.today = datetime.now().date()
        self.current_date = self.today
        
        self._create_date_controls()
        self._create_main_content()
        
        self.load_activities()
        self.load_todos()

    def _setup_window(self):
        self.master.title("Activity Tracker")
        default_font = ('JetBrains Mono', 10)
        self.master.option_add("*Font", default_font)
        self.master.configure(bg='#2C2C2C')
        self.master.attributes('-alpha', 0.9)

    def _create_date_controls(self):
        date_frame = tk.Frame(self.master, bg='#2C2C2C')
        date_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky='ew')
        
        self.date_label = tk.Label(date_frame, text=self.current_date.strftime("%d-%m-%Y"), 
                                   font=('JetBrains Mono', 12, 'bold'), bg='#2C2C2C', fg='white')
        self.date_label.pack(side=tk.LEFT, padx=10)
        
        for text, command in [("<", self.prev_date), (">", self.next_date), ("Today", self.go_to_today)]:
            btn = tk.Button(date_frame, text=text, command=command, 
                           font=('JetBrains Mono', 10), bg='#404040', fg='white', 
                           activebackground='#505050', border=0, padx=10)
            btn.pack(side=tk.LEFT, padx=5)

    def _create_main_content(self):
        # Main container
        main_frame = tk.Frame(self.master, bg='#2C2C2C')
        main_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        
        # Configure grid weights
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)
        main_frame.columnconfigure(2, weight=0)
        main_frame.columnconfigure(3, weight=1)
        
        self._create_activity_grid(main_frame)
        self._create_legend(main_frame)
        self._create_habits_section(main_frame)
        self._create_todo_section(main_frame)

    def _create_activity_grid(self, parent):
        activity_frame = tk.Frame(parent, bg='#2C2C2C')
        activity_frame.grid(row=0, column=0, padx=10, pady=10, sticky='n')
        
        tk.Label(activity_frame, text="Activities", font=('JetBrains Mono', 12, 'bold'),
                bg='#2C2C2C', fg='white').grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        self.entries = {}
        for hour in range(24):
            tk.Label(activity_frame, text=f"{hour:02d}:00", 
                    bg='#2C2C2C', fg='white').grid(row=hour+1, column=0, sticky='w', padx=(0, 5))
            
            entry = tk.Entry(activity_frame, width=5, font=('JetBrains Mono', 10),
                           bg='#404040', fg='white', insertbackground='white')
            entry.grid(row=hour+1, column=1, pady=1)
            entry.bind("<FocusOut>", lambda e, h=hour: self.save_activity(h, e.widget.get().lower()))
            entry.bind("<KeyRelease>", lambda e, h=hour: self.auto_advance_activity(h, e))
            
            self.entries[hour] = entry

    def _create_legend(self, parent):
        self.legend = {
            '1': 'sleep', '2': 'neutral', '3': 'productive', '4': 'waste', 
            '5': 'exercise', '6': 'university', '7': 'social', '8': 'reading', 
            '9': 'study', '10': 'transit', '11': 'work'
        }
        
        legend_frame = tk.Frame(parent, bg='#2C2C2C')
        legend_frame.grid(row=0, column=1, padx=10, pady=10, sticky='n')
        
        tk.Label(legend_frame, text="Activity Legend:", font=('JetBrains Mono', 12, 'bold'),
                bg='#2C2C2C', fg='white').pack(anchor='w')
        
        for key, value in self.legend.items():
            tk.Label(legend_frame, text=f"{key} - {value}", 
                    bg='#2C2C2C', fg='white').pack(anchor='w')

    def _create_habits_section(self, parent):
        habits_frame = tk.Frame(parent, bg='#2C2C2C')
        habits_frame.grid(row=0, column=2, padx=10, pady=10, sticky='n')
        
        tk.Label(habits_frame, text="Habits", font=('JetBrains Mono', 12, 'bold'),
                bg='#2C2C2C', fg='white').pack(anchor='w')
        
        existing_habits = get_habit_names() or [
            'wake_up_7', 'study', 'project', 'github', 'exercise', 'productive_day', 
            'journal', 'reading', 'plan_tomorrow', 'go_to_bed_22'
        ]
        
        for habit in existing_habits:
            create_habit_table(habit)
        
        self._initialize_habits_for_date(existing_habits)        
        
        self.habit_vars = {}
        self.habit_checkboxes = {}
        
        for habit in existing_habits:
            var = tk.BooleanVar()
            self.habit_vars[habit] = var
            
            current_date = self.current_date.strftime("%d-%m-%Y")
            habit_status = check_habit_status(habit, current_date)
            
            if habit_status is not None:
                var.set(habit_status)
            
            checkbox = tk.Checkbutton(
                habits_frame, 
                text=habit, 
                variable=var, 
                font=('JetBrains Mono', 10),
                bg='#2C2C2C', fg='white', selectcolor='#404040',
                activebackground='#2C2C2C', activeforeground='white',
                command=lambda h=habit: self.save_habit_status(h)
            )
            checkbox.pack(anchor='w')
            self.habit_checkboxes[habit] = checkbox

    def _create_todo_section(self, parent):
        todo_frame = tk.Frame(parent, bg='#2C2C2C')
        todo_frame.grid(row=0, column=3, padx=10, pady=10, sticky='nsew')
        
        # Header with add button
        header_frame = tk.Frame(todo_frame, bg='#2C2C2C')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text="Todo List", font=('JetBrains Mono', 12, 'bold'),
                bg='#2C2C2C', fg='white').pack(side='left')
        
        add_btn = tk.Button(header_frame, text="+", command=self.add_todo,
                          font=('JetBrains Mono', 12, 'bold'), bg='#404040', fg='white',
                          activebackground='#505050', border=0, padx=10)
        add_btn.pack(side='right')
        
        # Scrollable todo list
        self.todo_frame = tk.Frame(todo_frame, bg='#2C2C2C')
        self.todo_frame.pack(fill='both', expand=True)
        
        # Store todo widgets
        self.todo_widgets = []

    def _initialize_habits_for_date(self, habits):
        current_date = self.current_date.strftime("%d-%m-%Y")
        for habit in habits:
            if check_habit_status(habit, current_date) is None:
                add_habit_status(habit, current_date, False)

    def load_activities(self):
        for hour in range(24):
            activity = check_activity(self.current_date.strftime("%d-%m-%Y"), str(hour))
            self.entries[hour].delete(0, tk.END)
            if activity:
                self.entries[hour].insert(0, activity)

    def load_todos(self):
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
        task_text = simpledialog.askstring("Add Task", "Enter task:")
        if task_text and task_text.strip():
            current_date = self.current_date.strftime("%d-%m-%Y")
            add_task(current_date, task_text.strip(), False)
            self.load_todos()

    def edit_todo(self, todo_id, current_text):
        new_text = simpledialog.askstring("Edit Task", "Edit task:", initialvalue=current_text)
        if new_text and new_text.strip():
            update_task_text(todo_id, new_text.strip())
            self.load_todos()

    def delete_todo(self, todo_id):
        if messagebox.askyesno("Delete Task", "Are you sure you want to delete this task?"):
            delete_task(todo_id)
            self.load_todos()

    def toggle_todo(self, todo_id, completed):
        update_task_status(todo_id, completed)
        self.load_todos()

    def auto_advance_activity(self, hour, event):
        """Auto-advance to next activity entry after typing a valid character."""
        entry = event.widget
        content = entry.get().lower()
        
        # If user typed a single valid character, save and move to next
        if len(content) == 1 and content in self.legend:
            self.save_activity(hour, content)
            
            # Move to next hour (if not the last hour)
            if hour < 23:
                self.entries[hour + 1].focus_set()
        
        # If user typed an invalid character or too many characters, clear and stay
        elif len(content) == 1 and content not in self.legend:
            messagebox.showerror("Error", "Invalid activity code. Use codes from the legend.")
            entry.delete(0, tk.END)
        elif len(content) > 1:
            # Keep only the first character if it's valid
            if content[0] in self.legend:
                entry.delete(1, tk.END)
                self.save_activity(hour, content[0])
                if hour < 23:
                    self.entries[hour + 1].focus_set()
            else:
                messagebox.showerror("Error", "Invalid activity code. Use codes from the legend.")
                entry.delete(0, tk.END)

    def save_activity(self, hour, activity):
        """Save activity and handle validation."""
        if not activity:  # Empty activity is allowed
            current_date = self.current_date.strftime("%d-%m-%Y")
            add_activity(current_date, str(hour), activity)
            return
            
        if len(activity) > 2:
            messagebox.showerror("Error", "Please enter only one or two characters.")
            self.entries[hour].delete(0, tk.END)
            return
        
        if activity and activity not in self.legend:
            messagebox.showerror("Error", "Invalid activity code. Use codes from the legend.")
            self.entries[hour].delete(0, tk.END)
            return
        
        current_date = self.current_date.strftime("%d-%m-%Y")
        add_activity(current_date, str(hour), activity)

    def save_habit_status(self, habit):
        current_date = self.current_date.strftime("%d-%m-%Y")
        status = self.habit_vars[habit].get()
        add_habit_status(habit, current_date, status)

    def _update_date_display(self):
        self.date_label.config(text=self.current_date.strftime("%d-%m-%Y"))
        self.load_activities()
        self.load_todos()
        
        # Initialize habits for the new date if needed
        existing_habits = list(self.habit_vars.keys())
        self._initialize_habits_for_date(existing_habits)
        
        # Update habit checkboxes
        for habit in self.habit_vars:
            current_date = self.current_date.strftime("%d-%m-%Y")
            habit_status = check_habit_status(habit, current_date)
            
            self.habit_vars[habit].set(habit_status if habit_status is not None else False)

    def prev_date(self):
        self.current_date -= timedelta(days=1)
        self._update_date_display()

    def next_date(self):
        self.current_date += timedelta(days=1)
        self._update_date_display()

    def go_to_today(self):
        self.current_date = self.today
        self._update_date_display()

def main():
    root = tk.Tk()
    root.geometry("800x600")
    root.minsize(800, 600)
    ActivityTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
