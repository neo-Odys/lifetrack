import tkinter as tk
from tkinter import messagebox
from database import add_activity, check_activity

class ActivityTracker:
    def __init__(self, parent, current_date, update_callback=None):
        self.parent = parent
        self.current_date = current_date
        self.update_callback = update_callback
        self.entries = {}
        self.legend = {
            '1': 'sleep', '2': 'neutral', '3': 'productive', '4': 'waste', 
            '5': 'exercise', '6': 'university', '7': 'social', '8': 'reading', 
            '9': 'study', '10': 'transit', '11': 'work'
        }
        self.create_widgets()
        self.load_activities()

    def create_widgets(self):
        # Main frame for activities
        self.main_frame = tk.Frame(self.parent, bg='#2C2C2C')
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        
        # Title
        tk.Label(self.main_frame, text="Activities", font=('JetBrains Mono', 12, 'bold'),
                bg='#2C2C2C', fg='white').pack(pady=(0, 10))
        
        # Activity grid
        activity_frame = tk.Frame(self.main_frame, bg='#2C2C2C')
        activity_frame.pack()
        
        for hour in range(24):
            tk.Label(activity_frame, text=f"{hour:02d}:00", 
                    bg='#2C2C2C', fg='white').grid(row=hour, column=0, sticky='w', padx=(0, 5))
            
            entry = tk.Entry(activity_frame, width=5, font=('JetBrains Mono', 10),
                           bg='#404040', fg='white', insertbackground='white')
            entry.grid(row=hour, column=1, pady=1)
            entry.bind("<FocusOut>", lambda e, h=hour: self.save_activity(h, e.widget.get().lower()))
            entry.bind("<KeyRelease>", lambda e, h=hour: self.auto_advance_activity(h, e))
            
            self.entries[hour] = entry

    def create_legend_widget(self, parent):
        """Create legend widget for external use"""
        legend_frame = tk.Frame(parent, bg='#2C2C2C')
        
        tk.Label(legend_frame, text="Activity Legend:", font=('JetBrains Mono', 12, 'bold'),
                bg='#2C2C2C', fg='white').pack(anchor='w')
        
        for key, value in self.legend.items():
            tk.Label(legend_frame, text=f"{key} - {value}", 
                    bg='#2C2C2C', fg='white').pack(anchor='w')
        
        return legend_frame

    def load_activities(self):
        """Load activities for the current date"""
        for hour in range(24):
            activity = check_activity(self.current_date.strftime("%d-%m-%Y"), str(hour))
            self.entries[hour].delete(0, tk.END)
            if activity:
                self.entries[hour].insert(0, activity)

    def update_date(self, new_date):
        """Update current date and reload activities"""
        self.current_date = new_date
        self.load_activities()

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
            if self.update_callback:
                self.update_callback()
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
        
        if self.update_callback:
            self.update_callback()