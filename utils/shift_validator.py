from datetime import datetime, timedelta
from typing import List
import pandas as pd

class ShiftValidator:
    @staticmethod
    def check_eleven_hour_rule(employee_id: int, shifts_df: pd.DataFrame, new_shift_start: datetime) -> bool:
        """Check if there's at least 11 hours between shifts"""
        employee_shifts = shifts_df[shifts_df['employee_id'] == employee_id]
        for _, shift in employee_shifts.iterrows():
            time_diff = abs((new_shift_start - shift['end_time']).total_seconds() / 3600)
            if time_diff < 11:
                return False
        return True
    
    @staticmethod
    def check_weekly_hours(employee_id: int, shifts_df: pd.DataFrame, week_start: datetime) -> float:
        """Calculate total working hours in a week"""
        week_end = week_start + timedelta(days=7)
        week_shifts = shifts_df[
            (shifts_df['employee_id'] == employee_id) &
            (shifts_df['date'] >= week_start) &
            (shifts_df['date'] < week_end)
        ]
        
        total_hours = sum(
            (shift['end_time'] - shift['start_time']).total_seconds() / 3600
            for _, shift in week_shifts.iterrows()
        )
        return total_hours
    
    @staticmethod
    def validate_off_days(employee_id: int, shifts_df: pd.DataFrame, week_start: datetime) -> bool:
        """Ensure employee has required OFF days"""
        week_end = week_start + timedelta(days=7)
        week_shifts = shifts_df[
            (shifts_df['employee_id'] == employee_id) &
            (shifts_df['date'] >= week_start) &
            (shifts_df['date'] < week_end)
        ]
        
        off_days = 7 - len(week_shifts)
        return off_days >= 2  # Minimum 2 OFF days per week
