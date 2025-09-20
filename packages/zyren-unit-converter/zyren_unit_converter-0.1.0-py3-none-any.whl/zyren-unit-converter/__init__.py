# لتسهيل الاستيراد من الوحدة
# __init__.py
"""
واجهة مكتبة unit_converter
تجمع جميع التحويلات في مكان واحد
"""

# استدعاء دوال التحويل من الملفات المختلفة
from .length import convert_length
from .weight import convert_weight
from .volume import convert_volume
from .temperature import convert_temperature
from .time import convert_time

# تحديد ما سيتم استيراده عند استخدام 'from unit_converter import *'
__all__ = [
    "convert_length",
    "convert_weight",
    "convert_volume",
    "convert_temperature",
    "convert_time"
]
