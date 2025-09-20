# تحويلات الحرارة
# temperature.py
"""
ملف تحويلات الحرارة
يدعم الوحدات التالية:
- Celsius (°C)
- Fahrenheit (°F)
- Kelvin (K)
- Rankine (°R) (اختياري)
"""

def convert_temperature(value, from_unit, to_unit):
    """
    دالة تحويل الحرارة
    value: القيمة المراد تحويلها
    from_unit: الوحدة الأصلية ('C', 'F', 'K', 'R')
    to_unit: الوحدة المطلوبة التحويل إليها ('C', 'F', 'K', 'R')
    """
    # تحويل كل وحدة أولًا إلى سيليزية (Celsius)
    if from_unit == "C":
        temp_c = value
    elif from_unit == "F":
        temp_c = (value - 32) * 5/9
    elif from_unit == "K":
        temp_c = value - 273.15
    elif from_unit == "R":
        temp_c = (value - 491.67) * 5/9
    else:
        raise ValueError(f"الوحدة الأصلية '{from_unit}' غير مدعومة")

    # التحويل من السيليزية للوحدة المطلوبة
    if to_unit == "C":
        return temp_c
    elif to_unit == "F":
        return temp_c * 9/5 + 32
    elif to_unit == "K":
        return temp_c + 273.15
    elif to_unit == "R":
        return (temp_c + 273.15) * 9/5
    else:
        raise ValueError(f"الوحدة المطلوبة '{to_unit}' غير مدعومة")
