from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Employee:
    id: int
    name: str
    location: str  # Amasya or Istanbul
    district: Optional[str]  # For Istanbul: Anadolu/Avrupa
    special_condition: Optional[str]  # Pregnancy, disability etc.
    service_route: Optional[str]
    hire_date: datetime
    
    def can_work_night_shift(self) -> bool:
        if self.special_condition in ['Hamile', 'Engelli']:
            return False
        return True
    
    def get_allowed_shift_types(self) -> list:
        allowed_shifts = []
        
        if self.location == 'Amasya':
            allowed_shifts = ['08:00-17:00', '09:00-18:00', '11:00-22:00']
        else:  # Istanbul
            allowed_shifts = ['08:00-17:00', '15:00-00:00']
            
        if self.special_condition == 'Hamile':
            return ['09:00-18:00']
        elif self.special_condition == 'Engelli':
            return ['08:00-17:00', '09:00-18:00']
            
        return allowed_shifts
