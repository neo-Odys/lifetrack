import tkinter as tk
from database import (
    create_habit_table, add_habit_status, check_habit_status, get_habit_names
)

class HabitsTracker:
    def __init__(self, parent, current_date, update_callback=None):
        self.parent = parent
        self.current_date = current_date
        self.update_callback = update_callback
        self.habit_vars = {}
        self.habit_checkboxes = {}
        self.create_widgets()
        self.load_habits()

    def create_widgets(self):
        # Main frame for habits
        self.main_frame = tk.Frame(self.parent, bg='#2C2C2C')
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        
        # Title
        tk.Label(self.main_frame, text="Habits", font=('JetBrains Mono', 12, 'bold'),
                bg='#2C2C2C', fg='white').pack(anchor='w', pady=(0, 10))
        
        # Habits container
        self.habits_container = tk.Frame(self.main_frame, bg='#2C2C2C')
        self.habits_container.pack(fill=tk.BOTH, expand=True)

    def load_habits(self):
        """Load and display habits"""
        # Clear existing widgets
        for widget in self.habits_container.winfo_children():
            widget.destroy()
        
        self.habit_vars.clear()
        self.habit_checkboxes.clear()
        
        # Get existing habits or create default ones
        existing_habits = get_habit_names() or [
            'wake_up_7', 'study', 'project', 'github', 'exercise', 'productive_day', 
            'journal', 'reading', 'plan_tomorrow', 'go_to_bed_22'
        ]
        
        # Create habit tables if they don't exist
        for habit in existing_habits:
            create_habit_table(habit)
        
        # Initialize habits for current date
        self._initialize_habits_for_date(existing_habits)
        
        # Create checkboxes
        for habit in existing_habits:
            var = tk.BooleanVar()
            self.habit_vars[habit] = var
            
            current_date = self.current_date.strftime("%d-%m-%Y")
            habit_status = check_habit_status(habit, current_date)
            
            if habit_status is not None:
                var.set(habit_status)
            
            checkbox = tk.Checkbutton(
                self.habits_container, 
                text=habit, 
                variable=var, 
                font=('JetBrains Mono', 10),
                bg='#2C2C2C', fg='white', selectcolor='#404040',
                activebackground='#2C2C2C', activeforeground='white',
                command=lambda h=habit: self.save_habit_status(h)
            )
            checkbox.pack(anchor='w')
            self.habit_checkboxes[habit] = checkbox

    def _initialize_habits_for_date(self, habits):
        """Initialize habits for the current date if they don't exist"""
        current_date = self.current_date.strftime("%d-%m-%Y")
        for habit in habits:
            if check_habit_status(habit, current_date) is None:
                add_habit_status(habit, current_date, False)

    def save_habit_status(self, habit):
        """Save habit status to database"""
        current_date = self.current_date.strftime("%d-%m-%Y")
        status = self.habit_vars[habit].get()
        add_habit_status(habit, current_date, status)
        
        if self.update_callback:
            self.update_callback()

    def update_date(self, new_date):
        """Update current date and reload habits"""
        self.current_date = new_date
        
        # Initialize habits for the new date if needed
        existing_habits = list(self.habit_vars.keys())
        self._initialize_habits_for_date(existing_habits)
        
        # Update habit checkboxes
        for habit in self.habit_vars:
            current_date = self.current_date.strftime("%d-%m-%Y")
            habit_status = check_habit_status(habit, current_date)
            
            self.habit_vars[habit].set(habit_status if habit_status is not None else False)