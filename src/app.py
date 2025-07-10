import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from database import (
    add_activity, check_activity, create_habit_table, 
    add_habit_status, check_habit_status, get_habit_names
)

class ActivityTracker:
    def __init__(self, master):
        self.master = master
        self._setup_window()
        
        self.today = datetime.now().date()
        self.current_date = self.today
        
        self._create_date_controls()
        self._create_activity_grid()
        self._create_legend()
        self._create_habits_section()
        
        self.load_activities()

    def _setup_window(self):
        self.master.title("Activity Tracker")
        default_font = ('JetBrains Mono', 10)
        self.master.option_add("*Font", default_font)
        self.master.configure(bg='#2C2C2C')
        self.master.attributes('-alpha', 0.9)

    def _create_date_controls(self):
        date_frame = tk.Frame(self.master)
        date_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=5)
        
        self.date_label = tk.Label(date_frame, text=self.current_date.strftime("%d-%m-%Y"), 
                                   font=('JetBrains Mono', 12, 'bold'))
        self.date_label.pack(side=tk.LEFT, padx=10)
        
        for text, command in [("<", self.prev_date), (">", self.next_date), ("Today", self.go_to_today)]:
            tk.Button(date_frame, text=text, command=command).pack(side=tk.LEFT, padx=5)

    def _create_activity_grid(self):
        activity_frame = tk.Frame(self.master)
        activity_frame.grid(row=1, column=0, padx=10, pady=10)
        
        self.entries = {}
        for hour in range(24):
            tk.Label(activity_frame, text=f"{hour:02d}:00").grid(row=hour, column=0)
            
            entry = tk.Entry(activity_frame, width=5)
            entry.grid(row=hour, column=1)
            entry.bind("<FocusOut>", lambda e, h=hour: self.save_activity(h, e.widget.get().lower()))
            
            self.entries[hour] = entry

    def _create_legend(self):
        self.legend = {
            '1': 'sleep', '2': 'neutral', '3': 'productive', '4': 'waste', 
            '5': 'exercise', '6': 'university', '7': 'social', '8': 'reading', 
            '9': 'study', '10': 'transit', '11': 'work'
        }
        
        legend_frame = tk.Frame(self.master)
        legend_frame.grid(row=1, column=2, padx=10, pady=10, sticky='n')
        
        tk.Label(legend_frame, text="Activity Legend:", font=('JetBrains Mono', 12, 'bold')).pack(anchor='w')
        
        for key, value in self.legend.items():
            tk.Label(legend_frame, text=f"{key} - {value}").pack(anchor='w')

    def _create_habits_section(self):
        habits_frame = tk.Frame(self.master)
        habits_frame.grid(row=1, column=3, padx=10, pady=10, sticky='n')
        
        tk.Label(habits_frame, text="Habits", font=('JetBrains Mono', 12, 'bold')).pack(anchor='w')
        
        existing_habits = get_habit_names() or [
            'wake_up_7','study', 'project', 'github', 'exercise', 'productive_day', 
            'journal', 'reading', 'plan_tommorow', 'go_to_bed_22'
        ]
        
        for habit in existing_habits:
            create_habit_table(habit)
        
        self._initialize_habits_for_today(existing_habits)        
        
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
                command=lambda h=habit: self.save_habit_status(h)
            )
            checkbox.pack(anchor='w')
            self.habit_checkboxes[habit] = checkbox

    def _initialize_habits_for_today(self, habits):
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

    def save_activity(self, hour, activity):
        if len(activity) > 1:
            messagebox.showerror("Error", "Please enter only one letter.")
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
    root.geometry("400x800")
    ActivityTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()


