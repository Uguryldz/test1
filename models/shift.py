from dataclasses import dataclass
from datetime import datetime, time

@dataclass
class Shift:
    employee_id: int
    date: datetime
    shift_type: str
    start_time: time
    end_time: time
    
    @staticmethod
    def get_shift_types(location: str) -> dict:
        if location == 'Amasya':
            return {
                'Sabah': ('08:00-17:00', time(8), time(17)),
                'Normal': ('09:00-18:00', time(9), time(18)),
                'Akşam': ('11:00-22:00', time(11), time(22)),
                'Gece': ('00:00-08:00', time(0), time(8))
            }
        else:  # Istanbul
            return {
                'Gündüz': ('08:00-17:00', time(8), time(17)),
                'Akşam': ('15:00-00:00', time(15), time(0)),
                'Gece': ('00:00-08:00', time(0), time(8))
            }
