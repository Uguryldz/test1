import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

class AdvancedShiftOptimizer:
    def __init__(self):
        self.shift_counts = defaultdict(lambda: defaultdict(int))  # Çalışan bazlı vardiya sayaçları
        self.location_groups = defaultdict(list)  # Yaka bazlı çalışan grupları

        self.shift_requirements = {
            '08:00-17:00': 4,
            '09:00-18:00': 7,
            '11:00-22:00': 9,
            '15:00-00:00': 6,
            '00:00-08:00': 2
        }

        self.location_shifts = {
            'Amasya-1': ['08:00-17:00', '09:00-18:00', '11:00-22:00'],
            'Amasya 2-A': ['08:00-17:00', '09:00-18:00', '11:00-22:00'],
            'Amasya 2-B': ['08:00-17:00', '09:00-18:00', '11:00-22:00'],
            'Amasya 3': ['08:00-17:00', '09:00-18:00', '11:00-22:00']
        }

    def initialize_groups(self, employees_df: pd.DataFrame):
        """Çalışanları yakalarına göre grupla"""
        for location in self.location_shifts.keys():
            self.location_groups[location] = employees_df[
                employees_df['location'] == location
            ]['id'].tolist()

    def calculate_shift_score(self, employee: pd.Series, shift_type: str, 
                            date: datetime, current_schedule: pd.DataFrame,
                            current_shift_employees: List[int]) -> float:
        """
        Vardiya ataması için gelişmiş skor hesaplama
        """
        score = 0.0

        # Temel uygunluk kontrolü
        if not self._is_shift_allowed(employee, shift_type, date):
            return -1000.0

        # 11 saat kuralı kontrolü
        if not self._check_eleven_hour_rule(employee['id'], current_schedule, shift_type, date):
            return -1000.0

        # Yaka bazlı grup skoru (aynı yakadan çalışanları tercih et)
        location_score = self._calculate_location_group_score(
            employee['id'], 
            employee['location'],
            current_shift_employees
        )
        score += location_score * 0.4

        # Vardiya dağılımı dengesi skoru
        distribution_score = self._calculate_distribution_score(
            employee['id'],
            shift_type
        )
        score += distribution_score * 0.4

        # İş yükü dengesi skoru
        workload_score = self._calculate_workload_score(
            employee['id'],
            current_schedule
        )
        score += workload_score * 0.2

        return score

    def _calculate_location_group_score(self, employee_id: int, location: str, 
                                     current_employees: List[int]) -> float:
        """
        Aynı yakadan çalışanlarla çalışma skoru
        """
        if not current_employees:
            return 1.0

        same_location_count = sum(
            1 for emp_id in current_employees 
            if emp_id in self.location_groups[location]
        )

        return same_location_count / len(current_employees)

    def _calculate_distribution_score(self, employee_id: int, shift_type: str) -> float:
        """
        Vardiya dağılımı dengesi için skor hesapla
        """
        total_shifts = sum(self.shift_counts[employee_id].values())
        if total_shifts == 0:
            return 1.0

        current_shift_count = self.shift_counts[employee_id][shift_type]
        average_shifts = total_shifts / len(self.shift_requirements)

        # Vardiya sayısı ortalamanın altındaysa yüksek skor
        if current_shift_count < average_shifts:
            return 1.0
        # Ortalamanın üstündeyse düşük skor
        return 0.5

    def _calculate_workload_score(self, employee_id: int, schedule: pd.DataFrame) -> float:
        """
        İş yükü dengesi için skor hesapla
        """
        weekly_hours = self._calculate_weekly_hours(employee_id, schedule)
        if weekly_hours > 45:  # Yasal sınır
            return 0.0
        if weekly_hours > 40:  # Normal mesai
            return 0.5
        return 1.0

    def optimize_weekly_schedule(self, employees_df: pd.DataFrame, 
                               start_date: datetime) -> pd.DataFrame:
        """
        Haftalık vardiya planını optimize et
        """
        self.initialize_groups(employees_df)
        schedule = []

        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)

            # Her vardiya tipi için optimizasyon yap
            for shift_type, required_count in self.shift_requirements.items():
                selected_employees = []

                while len(selected_employees) < required_count:
                    best_score = -float('inf')
                    best_employee = None

                    for _, employee in employees_df.iterrows():
                        if employee['id'] not in selected_employees:
                            score = self.calculate_shift_score(
                                employee,
                                shift_type,
                                current_date,
                                pd.DataFrame(schedule),
                                selected_employees
                            )

                            if score > best_score:
                                best_score = score
                                best_employee = employee['id']

                    if best_employee is None:
                        break

                    selected_employees.append(best_employee)
                    self.shift_counts[best_employee][shift_type] += 1

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

    def _is_shift_allowed(self, employee: pd.Series, shift_type: str, date: datetime) -> bool:
        """
        Vardiya kısıtlamalarını kontrol et
        """
        # Özel durum kontrolleri
        if employee['special_condition'] == 'Hamile':
            return shift_type == '09:00-18:00'
        elif employee['special_condition'] == 'Engelli':
            return shift_type in ['08:00-17:00', '09:00-18:00']

        # Lokasyon kontrolleri
        if employee['location'] in self.location_shifts:
            return shift_type in self.location_shifts[employee['location']]

        return False

    def _check_eleven_hour_rule(self, employee_id: int, schedule: pd.DataFrame, 
                             new_shift: str, date: datetime) -> bool:
        """
        11 saat kuralını kontrol et
        """
        if len(schedule) == 0:
            return True

        new_start = datetime.strptime(new_shift.split('-')[0], '%H:%M').time()
        new_start_dt = datetime.combine(date, new_start)

        employee_shifts = schedule[schedule['employee_id'] == employee_id]

        for _, shift in employee_shifts.iterrows():
            if shift['end_time']:
                shift_end_dt = datetime.combine(shift['date'], shift['end_time'])
                hours_diff = abs((new_start_dt - shift_end_dt).total_seconds() / 3600)
                if hours_diff < 11:
                    return False
        return True

    def _calculate_weekly_hours(self, employee_id: int, schedule: pd.DataFrame) -> float:
        """
        Haftalık çalışma saatlerini hesapla
        """
        if len(schedule) == 0:
            return 0.0

        total_hours = 0
        employee_shifts = schedule[schedule['employee_id'] == employee_id]

        for _, shift in employee_shifts.iterrows():
            if shift['start_time'] and shift['end_time']:
                start_dt = datetime.combine(shift['date'], shift['start_time'])
                end_dt = datetime.combine(shift['date'], shift['end_time'])
                hours = (end_dt - start_dt).total_seconds() / 3600
                total_hours += hours

        return total_hours