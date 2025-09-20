# volume.py
"""
ملف تحويلات الحجم / السعة
يدعم الوحدات الشائعة عالميًا:
- مليلتر، لتر، متر مكعب
- جالون، باينت، كوب، أونصة سائلة
"""

# جدول التحويلات بالنسبة لللتر (L)
conversion_factors = {
    "ml": 0.001,
    "l": 1,
    "m3": 1000,          # متر مكعب
    "tsp": 0.00492892,   # ملعقة صغيرة
    "tbsp": 0.0147868,   # ملعقة كبيرة
    "cup": 0.24,         # كوب
    "pt": 0.473176,      # باينت
    "qt": 0.946353,      # كوارتر
    "gal": 3.78541,      # جالون أمريكي
    "fl_oz": 0.0295735   # أونصة سائلة
}

def convert_volume(value, from_unit, to_unit):
    """
    دالة تحويل الحجم / السعة
    value: القيمة المراد تحويلها
    from_unit: الوحدة الأصلية ('ml', 'l', 'cup', ...)
    to_unit: الوحدة المطلوبة التحويل إليها
    """
    if from_unit not in conversion_factors:
        raise ValueError(f"الوحدة الأصلية '{from_unit}' غير مدعومة")
    if to_unit not in conversion_factors:
        raise ValueError(f"الوحدة المطلوبة '{to_unit}' غير مدعومة")

    # تحويل للوحدة الأساسية (لتر)
    value_in_liters = value * conversion_factors[from_unit]

    # التحويل للوحدة المطلوبة
    converted_value = value_in_liters / conversion_factors[to_unit]

    return converted_value
