# تحويلات الزمن
# time.py
"""
ملف تحويلات الزمن
يدعم الوحدات التالية:
- ثانية (s)
- دقيقة (min)
- ساعة (h)
- يوم (day)
- أسبوع (week)
- شهر (month) (30 يوم تقريبًا)
- سنة (year) (365 يوم تقريبًا)
"""

# جدول التحويلات بالنسبة للثانية (الوحدة الأساسية)
conversion_factors = {
    "s": 1,
    "min": 60,
    "h": 3600,
    "day": 86400,
    "week": 604800,
    "month": 2592000,  # 30 يوم
    "year": 31536000   # 365 يوم
}

def convert_time(value, from_unit, to_unit):
    """
    دالة تحويل الزمن
    value: القيمة المراد تحويلها
    from_unit: الوحدة الأصلية ('s', 'min', 'h', ...)
    to_unit: الوحدة المطلوبة التحويل إليها ('s', 'min', 'h', ...)
    """
    # التحقق من صحة الوحدات
    if from_unit not in conversion_factors:
        raise ValueError(f"الوحدة الأصلية '{from_unit}' غير مدعومة")
    if to_unit not in conversion_factors:
        raise ValueError(f"الوحدة المطلوبة '{to_unit}' غير مدعومة")

    # تحويل للوحدة الأساسية (ثانية)
    value_in_seconds = value * conversion_factors[from_unit]

    # التحويل للوحدة المطلوبة
    converted_value = value_in_seconds / conversion_factors[to_unit]

    return converted_value
