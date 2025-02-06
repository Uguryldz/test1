import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime, timedelta

class ShiftOptimizer:
    def __init__(self):
        # Vardiya başına minimum çalışan sayıları
        self.shift_requirements = {
            '08:00-17:00': 4,
            '09:00-18:00': 7,
            '11:00-22:00': 9,
            '15:00-00:00': 6,
            '00:00-08:00': 2
        }

        # Lokasyon bazlı kısıtlamalar
        self.location_constraints = {
            'Amasya': {
                'allowed_shifts': ['08:00-17:00', '09:00-18:00', '11:00-22:00'],
                'min_morning_staff': 3
            },
            'İstanbul': {
                'allowed_shifts': ['08:00-17:00', '15:00-00:00'],
                'weekend_policy': 'home_office'
            }
        }

    def create_weekly_schedule(self, employees_df: pd.DataFrame, start_date: datetime) -> pd.DataFrame:
        """Haftalık vardiya planı oluştur"""
        schedule = []
        days = ['Pazartesi', 'Sali', 'Carsamba', 'Persembe', 'Cuma', 'Cumartesi', 'Pazar']

        # Her gün için vardiya ataması yap
        for day_idx, day in enumerate(days):
            current_date = start_date + timedelta(days=day_idx)

            # İstanbul için Pazar günü OFF
            if day == 'Pazar':
                istanbul_employees = employees_df[employees_df['location'] == 'İstanbul']
                for _, emp in istanbul_employees.iterrows():
                    schedule.append({
                        'employee_id': emp['id'],
                        'date': current_date,
                        'shift_type': 'OFF',
                        'start_time': None,
                        'end_time': None
                    })
                continue

            # Her vardiya tipi için çalışan ata
            for shift_type, required_count in self.shift_requirements.items():
                available_employees = self._get_available_employees(
                    employees_df, 
                    schedule, 
                    current_date, 
                    shift_type
                )

                # Vardiyaya uygun çalışanları seç
                selected_employees = self._select_employees(
                    available_employees,
                    required_count,
                    shift_type,
                    current_date
                )

                # Seçilen çalışanları vardiyaya ata
                for emp_id in selected_employees:
                    schedule.append({
                        'employee_id': emp_id,
                        'date': current_date,
                        'shift_type': shift_type,
                        'start_time': datetime.strptime(shift_type.split('-')[0], '%H:%M').time(),
                        'end_time': datetime.strptime(shift_type.split('-')[1], '%H:%M').time()
                    })

        return pd.DataFrame(schedule)

    def _get_available_employees(self, employees_df: pd.DataFrame, 
                               current_schedule: List[Dict], 
                               date: datetime,
                               shift_type: str) -> List[int]:
        """Vardiya için uygun çalışanları belirle"""
        available_employees = []

        for _, employee in employees_df.iterrows():
            # Özel durum kontrolleri
            if not self._check_special_conditions(employee, shift_type):
                continue

            # Lokasyon kontrolü
            if not self._check_location_constraints(employee, shift_type, date):
                continue

            # 11 saat kuralı kontrolü
            if not self._check_eleven_hour_rule(employee['id'], current_schedule, shift_type, date):
                continue

            available_employees.append(employee['id'])

        return available_employees

    def _check_special_conditions(self, employee: pd.Series, shift_type: str) -> bool:
        """Çalışanın özel durumlarını kontrol et"""
        if employee['special_condition'] == 'Hamile':
            return shift_type == '09:00-18:00'
        elif employee['special_condition'] == 'Engelli':
            return shift_type not in ['00:00-08:00', '15:00-00:00']
        return True

    def _check_location_constraints(self, employee: pd.Series, shift_type: str, date: datetime) -> bool:
        """Lokasyon bazlı kısıtlamaları kontrol et"""
        location_shifts = self.location_constraints[employee['location']]['allowed_shifts']

        if employee['location'] == 'İstanbul':
            if date.weekday() in [5, 6]:  # Cumartesi ve Pazar
                return False

        return shift_type in location_shifts

    def _check_eleven_hour_rule(self, employee_id: int, schedule: List[Dict], 
                               new_shift: str, date: datetime) -> bool:
        """11 saat kuralını kontrol et"""
        new_start = datetime.strptime(new_shift.split('-')[0], '%H:%M').time()
        new_start_dt = datetime.combine(date, new_start)

        for shift in schedule:
            if shift['employee_id'] == employee_id:
                if shift['end_time']:
                    shift_end_dt = datetime.combine(shift['date'], shift['end_time'])
                    hours_diff = abs((new_start_dt - shift_end_dt).total_seconds() / 3600)
                    if hours_diff < 11:
                        return False
        return True

    def _select_employees(self, available_employees: List[int], 
                         required_count: int,
                         shift_type: str,
                         date: datetime) -> List[int]:
        """Vardiya için çalışan seç"""
        if len(available_employees) <= required_count:
            return available_employees

        # Rastgele seçim yap
        np.random.shuffle(available_employees)
        return available_employees[:required_count]