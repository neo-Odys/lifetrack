import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
from database import (
    get_habit_names, get_activities_by_date, check_habit_status
)

class StatsWidgets:
    def __init__(self):
        plt.style.use('dark_background')
        
    def create_habit_heatmap(self, parent, width=10, height=2):
        """Create GitHub-style habit completion heatmap."""
        fig, ax = plt.subplots(figsize=(width, height), facecolor='#2C2C2C')
        fig.patch.set_facecolor('#2C2C2C')
        ax.set_facecolor('#2C2C2C')
        
        # Get habit data for the last year, but only up to current week
        end_date = datetime.now().date()
        # Find the end of current week (Saturday)
        days_until_saturday = (5 - end_date.weekday()) % 7
        current_week_end = end_date + timedelta(days=days_until_saturday)
        
        start_date = current_week_end - timedelta(days=365)
        
        habits = get_habit_names()
        if not habits:
            ax.text(0.5, 0.5, 'No habit data available', 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=12, color='white')
        else:
            # Calculate completion percentages for each day
            date_scores = {}
            current_date = start_date
            
            while current_date <= current_week_end:
                date_str = current_date.strftime("%d-%m-%Y")
                completed_habits = sum(1 for habit in habits 
                                     if check_habit_status(habit, date_str))
                completion_rate = (completed_habits / len(habits)) if len(habits) > 0 else 0
                date_scores[current_date] = completion_rate
                current_date += timedelta(days=1)
            
            # Create GitHub-style calendar heatmap
            self._create_github_heatmap(ax, date_scores, start_date, current_week_end, end_date)
        
        plt.tight_layout()
        
        # Add canvas to frame
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return canvas
    
    def _create_github_heatmap(self, ax, date_scores, start_date, current_week_end, today):
        """Create a GitHub-style calendar heatmap."""
        # Find the first Sunday before start_date
        days_back = (start_date.weekday() + 1) % 7
        first_sunday = start_date - timedelta(days=days_back)
        
        # Create a grid for the calendar
        weeks = []
        current_week = []
        current_date = first_sunday
        
        while current_date <= current_week_end + timedelta(days=6):
            # Only show data up to today, future dates should be empty
            if current_date <= today:
                score = date_scores.get(current_date, 0)
            else:
                score = None  # Future dates
            current_week.append(score)
            
            if len(current_week) == 7:
                weeks.append(current_week)
                current_week = []
            
            current_date += timedelta(days=1)
        
        if current_week:
            while len(current_week) < 7:
                current_week.append(None)
            weeks.append(current_week)
        
        # Convert to numpy array (transpose for correct orientation)
        # Replace None with -1 to handle future dates differently
        processed_weeks = []
        for week in weeks:
            processed_week = []
            for day in week:
                if day is None:
                    processed_week.append(-1)  # Future date marker
                else:
                    processed_week.append(day)
            processed_weeks.append(processed_week)
        
        heatmap_data = np.array(processed_weeks).T
        
        # Create custom colormap (gray to green, with special color for future dates)
        colors = ['#21262d', '#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']
        from matplotlib.colors import ListedColormap
        cmap = ListedColormap(colors)
        
        # Create heatmap with discrete levels
        levels = [-1, 0, 0.2, 0.4, 0.6, 0.8, 1.0]
        norm = plt.matplotlib.colors.BoundaryNorm(levels, cmap.N)
        
        im = ax.imshow(heatmap_data, cmap=cmap, norm=norm, aspect='auto')
        
        # Customize appearance
        ax.set_title('Daily Habit Completion Heatmap', fontsize=11, color='white', pad=10)
        
        # Set day labels (left side)
        day_labels = ['S', 'M', 'T', 'W', 'T', 'F', 'S']
        ax.set_yticks(range(7))
        ax.set_yticklabels(day_labels, color='white', fontsize=8)
        
        # Set month labels (bottom) - only show every other month to avoid crowding
        month_positions = []
        month_labels = []
        current_date = first_sunday
        week_idx = 0
        
        while week_idx < len(weeks):
            if current_date.day <= 7:
                month_positions.append(week_idx)
                month_labels.append(current_date.strftime('%b'))
            current_date += timedelta(days=7)
            week_idx += 1
        
        # Show only every other month to avoid crowding
        filtered_positions = month_positions[::2]
        filtered_labels = month_labels[::2]
        
        ax.set_xticks(filtered_positions)
        ax.set_xticklabels(filtered_labels, color='white', fontsize=8)
        
        # Remove tick marks
        ax.tick_params(length=0)
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    def create_activity_pie_chart(self, parent, width=6, height=4):
        """Create activity breakdown pie chart."""
        fig, ax = plt.subplots(figsize=(width, height), facecolor='#2C2C2C')
        fig.patch.set_facecolor('#2C2C2C')
        
        # Get activity data for the last 30 days
        activity_counts = defaultdict(int)
        legend = {
            '1': 'Sleep', '2': 'Neutral', '3': 'Productive', '4': 'Waste',
            '5': 'Exercise', '6': 'University', '7': 'Social', '8': 'Reading',
            '9': 'Study', '10': 'Transit', '11': 'Work'
        }
        
        end_date = datetime.now().date()
        for i in range(30):
            current_date = end_date - timedelta(days=i)
            date_str = current_date.strftime("%d-%m-%Y")
            activities = get_activities_by_date(date_str)
            
            for hour, activity in activities:
                if activity in legend:
                    activity_counts[legend[activity]] += 1
        
        if not activity_counts:
            ax.text(0.5, 0.5, 'No activity data available', 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=12, color='white')
        else:
            # Create pie chart
            labels = list(activity_counts.keys())
            sizes = list(activity_counts.values())
            
            # Use a nice color palette
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                     '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471']
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                            colors=colors[:len(labels)], 
                                            startangle=90, textprops={'fontsize': 8})
            
            # Customize text colors
            for text in texts:
                text.set_color('white')
                text.set_fontsize(8)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(8)
            
            ax.set_title('Activity Breakdown (Last 30 Days)', 
                        fontsize=11, color='white', pad=10)
        
        plt.tight_layout()
        
        # Add canvas to frame
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return canvas
    
    def create_habit_progress_bars(self, parent):
        """Create progress bars for individual habits over the last 30 days."""
        habits = get_habit_names()
        if not habits:
            tk.Label(parent, text="No habit data available", 
                    bg='#2C2C2C', fg='white', font=('JetBrains Mono', 10)).pack()
            return
        
        # Calculate completion rates for each habit
        end_date = datetime.now().date()
        habit_completion = {}
        
        for habit in habits:
            completed_days = 0
            total_days = 0
            
            for i in range(30):
                current_date = end_date - timedelta(days=i)
                date_str = current_date.strftime("%d-%m-%Y")
                status = check_habit_status(habit, date_str)
                
                if status is not None:
                    total_days += 1
                    if status:
                        completed_days += 1
            
            if total_days > 0:
                habit_completion[habit] = (completed_days / total_days) * 100
        
        # Create progress bars
        for habit, completion_rate in habit_completion.items():
            # Habit name
            habit_frame = tk.Frame(parent, bg='#2C2C2C')
            habit_frame.pack(fill='x', pady=2)
            
            tk.Label(habit_frame, text=f"{habit}: {completion_rate:.1f}%", 
                    bg='#2C2C2C', fg='white', font=('JetBrains Mono', 9),
                    width=20, anchor='w').pack(side='left')
            
            # Progress bar
            progress_frame = tk.Frame(habit_frame, bg='#404040', height=10)
            progress_frame.pack(side='right', fill='x', expand=True, padx=(5, 0))
            
            # Progress fill
            fill_width = int(completion_rate)
            if fill_width > 0:
                fill_color = '#26a641' if completion_rate >= 70 else '#006d32' if completion_rate >= 50 else '#0e4429'
                progress_fill = tk.Frame(progress_frame, bg=fill_color, height=10)
                progress_fill.place(x=0, y=0, width=f"{fill_width}%", height=10)