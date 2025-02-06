import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from utils.config import SHIFT_CONFIG, SPECIAL_CONDITIONS, SERVICE_RULES

class AdvancedShiftOptimizer:
    def __init__(self):
        self.shift_counts = defaultdict(lambda: defaultdict(int))
        self.location_groups = defaultdict(list)
        self.config = SHIFT_CONFIG
        self.conn = psycopg2.connect(os.environ["DATABASE_URL"])

        # Veritabanından vardiya tiplerini al
        self.load_shift_requirements()

    def load_shift_requirements(self):
        """Veritabanından vardiya gereksinimlerini yükle"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM shift_types")
            shift_types = cur.fetchall()

        self.shift_requirements = {
            f"{row['start_time'].strftime('%H:%M')}-{row['end_time'].strftime('%H:%M')}": row['min_staff']
            for row in shift_types
        }

        # Lokasyon bazlı vardiyaları güncelle
        self.location_shifts = defaultdict(list)
        for row in shift_types:
            shift_time = f"{row['start_time'].strftime('%H:%M')}-{row['end_time'].strftime('%H:%M')}"
            self.location_shifts[row['location']].append(shift_time)

    def initialize_groups(self, employees_df: pd.DataFrame):
        """Çalışanları yakalarına göre grupla"""
        # Giriş tarihine göre sırala
        employees_df = employees_df.sort_values('hire_date')

        for location in self.location_shifts.keys():
            self.location_groups[location] = employees_df[
                employees_df['location'] == location
            ]['id'].tolist()

    def calculate_shift_score(self, employee: pd.Series, shift_type: str, 
                            date: datetime, current_schedule: pd.DataFrame,
                            current_shift_employees: List[int]) -> float:
        """Vardiya ataması için gelişmiş skor hesaplama"""
        score = 0.0

        if not self._is_shift_allowed(employee, shift_type, date):
            return -1000.0

        if not self._check_eleven_hour_rule(employee['id'], current_schedule, shift_type, date):
            return -1000.0

        # Çalışan giriş tarihi bazlı skor (daha eski çalışanlara öncelik)
        hire_date_score = self._calculate_hire_date_score(employee['hire_date'])
        score += hire_date_score * 0.3

        # Yaka bazlı grup skoru (aynı yakadan çalışanları tercih et)
        location_score = self._calculate_location_group_score(
            employee['id'], 
            employee['location'],
            current_shift_employees
        )
        score += location_score * 0.2

        # Vardiya dağılımı dengesi skoru
        distribution_score = self._calculate_distribution_score(
            employee['id'],
            shift_type
        )
        score += distribution_score * 0.3

        # Servis optimizasyonu skoru
        service_score = self._calculate_service_score(
            employee['location'],
            shift_type,
            current_shift_employees
        )
        score += service_score * 0.2

        # Peak saat optimizasyonu
        peak_score = self._calculate_peak_hour_score(
            employee['location'],
            shift_type,
            date
        )
        score += peak_score * 0.2


        return score

    def _calculate_hire_date_score(self, hire_date: datetime) -> float:
        """Çalışanın kıdemine göre skor hesapla"""
        days_employed = (datetime.now() - hire_date).days
        # Kıdem arttıkça skor azalır (yeni başlayanların vardiya sayısını dengelemek için)
        return 1.0 / (1.0 + np.log1p(days_employed))

    def _calculate_service_score(self, location: str, shift_type: str, 
                               current_employees: List[int]) -> float:
        """
        Servis optimizasyonu için skor hesapla
        """
        if location.startswith('Amasya'):
            shift_hour = int(shift_type.split(':')[0])
            # 20:00 sonrası vardiyalar için aynı güzergahtan çalışanları grupla
            if shift_hour >= 20 or (shift_hour + int(shift_type.split('-')[1].split(':')[0])) >= 20:
                return self._calculate_location_group_score(None, location, current_employees)
        return 1.0

    def _calculate_peak_hour_score(self, location: str, shift_type: str, date: datetime) -> float:
        """
        Peak saatlere göre skor hesapla
        """
        shift_start = datetime.strptime(shift_type.split('-')[0], '%H:%M').time()

        if location.startswith('Amasya'):
            peak_hours = self.config['peak_hours']['Amasya']['all_day']
        else:
            morning_peak = self.config['peak_hours']['Istanbul']['morning']
            evening_peak = self.config['peak_hours']['Istanbul']['evening']

            # Peak saatlerde daha yüksek skor
            if (morning_peak[0] <= shift_type <= morning_peak[1] or 
                evening_peak[0] <= shift_type <= evening_peak[1]):
                return 1.0
        return 0.5

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

        # Her gün için
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            daily_shifts = []

            # Her vardiya tipi için optimizasyon
            for shift_type, required_count in self.shift_requirements.items():
                selected_employees = []

                while len(selected_employees) < required_count:
                    best_score = -float('inf')
                    best_employee = None

                    # En uygun çalışanı seç
                    for _, employee in employees_df.iterrows():
                        if employee['id'] not in selected_employees:
                            # Günlük çakışma kontrolü
                            if len(daily_shifts) >= self.config['max_values']['daily_overlapping_shifts']:
                                continue

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
                    daily_shifts.append(best_employee)

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
        if employee['special_condition'] in SPECIAL_CONDITIONS:
            conditions = SPECIAL_CONDITIONS[employee['special_condition']]
            if shift_type not in conditions['allowed_shifts']:
                return False
            if conditions.get('no_night_shifts') and '00:00' in shift_type:
                return False

        # Lokasyon kontrolleri
        if employee['location'] in self.location_shifts:
            # Servis kısıtlamaları
            if employee['location'].startswith('Amasya'):
                shift_hour = int(shift_type.split(':')[0])
                if shift_hour < 20 and not SERVICE_RULES['Amasya']['morning_service']:
                    # 20:00 öncesi servis yoksa sadece belirli vardiyalar
                    return shift_type in ['08:00-17:00', '09:00-18:00']
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
                if hours_diff < self.config['min_hours_between_shifts']:
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