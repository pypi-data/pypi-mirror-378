# length.py
"""
ملف تحويلات الطول
يدعم التحويل بين الوحدات الشائعة عالميًا:
- متر، سنتيمتر، مليمتر، كيلومتر
- إنش، قدم، ياردة، ميل
- ميكرومتر، نانومتر، ميلي
- وحدة بحريّة (nautical mile)
"""

# جدول التحويلات بالنسبة للمتر
conversion_factors = {
    # وحدات مترية
    "m": 1,
    "cm": 0.01,
    "mm": 0.001,
    "km": 1000,
    "µm": 1e-6,     # ميكرومتر
    "nm": 1e-9,     # نانومتر
    # وحدات إنجليزية / أمريكية
    "inch": 0.0254,
    "ft": 0.3048,
    "yd": 0.9144,   # ياردة
    "mile": 1609.34,
    "nmi": 1852     # ميل بحري
}

def convert_length(value, from_unit, to_unit):
    """
    دالة تحويل الطول
    value: القيمة المراد تحويلها
    from_unit: الوحدة الأصلية (مثل 'm', 'cm', 'inch', ...)
    to_unit: الوحدة المطلوبة التحويل إليها
    """
    # التحقق من صحة الوحدات
    if from_unit not in conversion_factors:
        raise ValueError(f"الوحدة الأصلية '{from_unit}' غير مدعومة")
    if to_unit not in conversion_factors:
        raise ValueError(f"الوحدة المطلوبة '{to_unit}' غير مدعومة")

    # تحويل القيمة للوحدة الأساسية (متر)
    value_in_meters = value * conversion_factors[from_unit]

    # تحويل القيمة من الوحدة الأساسية للوحدة المطلوبة
    converted_value = value_in_meters / conversion_factors[to_unit]

    return converted_value
