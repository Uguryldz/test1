"""
Vardiya planlama sistemi için yapılandırma dosyası.
Tüm parametrik değerler burada tutulur.
"""

SHIFT_CONFIG = {
    # Minimum çalışan gereksinimleri
    'min_staff': {
        'morning': 3,  # Sabah vardiyası minimum çalışan
        'afternoon': 2,  # Öğlen vardiyası minimum çalışan
        'evening': 2,  # Akşam vardiyası minimum çalışan
        'night': 3,  # Gece vardiyası minimum çalışan (en az 1'i İstanbul'dan)
    },
    
    # Maksimum değerler
    'max_values': {
        'daily_overlapping_shifts': 45,  # Günlük maksimum çakışan vardiya
        'weekly_hours': 45,  # Haftalık maksimum çalışma saati
        'overtime_hours_yearly': 270,  # Yıllık maksimum fazla mesai
    },
    
    # Vardiya dağılım hedefleri (%)
    'shift_distribution': {
        'morning': 40,  # Sabah vardiyası hedef dağılım
        'afternoon': 30,  # Ara vardiya hedef dağılım
        'evening': 20,  # Akşam vardiyası hedef dağılım
        'night': 10,  # Gece vardiyası hedef dağılım
    },
    
    # Lokasyon bazlı özel kurallar
    'location_rules': {
        'Amasya-1': {
            'min_morning_staff': 3,
            'service_after_20': True,
        },
        'Amasya 2-A': {
            'min_morning_staff': 3,
            'service_after_20': True,
        },
        'Amasya 2-B': {
            'min_morning_staff': 3,
            'service_after_20': True,
        },
        'Amasya 3': {
            'min_morning_staff': 3,
            'service_after_20': True,
        }
    },
    
    # Vardiya arası minimum süre (saat)
    'min_hours_between_shifts': 11,
    
    # Peak saatler
    'peak_hours': {
        'Istanbul': {
            'morning': ('08:00', '10:00'),
            'evening': ('17:00', '19:00')
        },
        'Amasya': {
            'all_day': ('09:00', '18:00')
        }
    }
}

# Özel durumlar için kısıtlamalar
SPECIAL_CONDITIONS = {
    'Hamile': {
        'allowed_shifts': ['09:00-18:00'],
        'max_weekly_hours': 45,
        'no_night_shifts': True
    },
    'Engelli': {
        'allowed_shifts': ['08:00-17:00', '09:00-18:00'],
        'max_weekly_hours': 45,
        'no_night_shifts': True,
        'no_revisions': True
    },
    'Doğum Sonrası': {
        'allowed_shifts': ['08:00-17:00', '09:00-18:00'],
        'duration': '1 year',
        'no_night_shifts': True
    }
}

# Servis kısıtlamaları
SERVICE_RULES = {
    'Amasya': {
        'morning_service': False,  # 20:00 öncesi servis yok
        'evening_service': True,   # 20:00 sonrası servis var
        'service_routes': ['Amasya-1', 'Amasya 2-A', 'Amasya 2-B', 'Amasya 3']
    }
}
