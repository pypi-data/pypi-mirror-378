# تحويلات الوزن / الكتلة
# weight.py
"""
ملف تحويلات الوزن / الكتلة
يدعم الوحدات الشائعة عالميًا:
- غرام، كيلوجرام، طن
- باوند، أونصة
- ميليغرام، ميكروغرام
"""

# جدول التحويلات بالنسبة للغرام (g)
conversion_factors = {
    "mg": 0.001,
    "g": 1,
    "kg": 1000,
    "ton": 1_000_000,   # طن متري
    "lb": 453.592,      # باوند
    "oz": 28.3495,      # أونصة
    "µg": 1e-6          # ميكروغرام
}

def convert_weight(value, from_unit, to_unit):
    """
    دالة تحويل الوزن
    value: القيمة المراد تحويلها
    from_unit: الوحدة الأصلية ('g', 'kg', 'lb', ...)
    to_unit: الوحدة المطلوبة التحويل إليها
    """
    if from_unit not in conversion_factors:
        raise ValueError(f"الوحدة الأصلية '{from_unit}' غير مدعومة")
    if to_unit not in conversion_factors:
        raise ValueError(f"الوحدة المطلوبة '{to_unit}' غير مدعومة")

    # تحويل للوحدة الأساسية (غرام)
    value_in_grams = value * conversion_factors[from_unit]

    # التحويل للوحدة المطلوبة
    converted_value = value_in_grams / conversion_factors[to_unit]

    return converted_value
