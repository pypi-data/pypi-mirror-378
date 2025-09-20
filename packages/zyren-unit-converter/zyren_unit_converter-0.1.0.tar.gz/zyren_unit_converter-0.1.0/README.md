# Unit Converter 🐍

**Unit Converter** هي مكتبة بايثون مرنة وقوية لتحويل الوحدات العلمية والحياتية بسهولة ودقة.  
تم تصميم المكتبة لتكون مفيدة للطلاب، الباحثين، والمستخدمين العاديين على حد سواء.

---

## 🔹 المميزات
- تحويل بين وحدات الطول، الوزن، الحجم، الزمن، والحرارة.  
- مرونة كاملة: يمكن للمستخدم اختيار أي وحدة أصلية وأي وحدة للتحويل.  
- تغطي أغلب الوحدات الشائعة عالميًا.  
- تصميم بسيط وواضح يسهل التوسعة والصيانة.  

---

## 🔹 الوحدات المدعومة

### **الطول (Length)**
- متر (m), سنتيمتر (cm), مليمتر (mm), كيلومتر (km)  
- إنش (inch), قدم (ft), ياردة (yd), ميل (mile), ميل بحري (nmi)  
- ميكرومتر (µm), نانومتر (nm)  

### **الوزن / الكتلة (Weight)**
- ميليغرام (mg), غرام (g), كيلوجرام (kg), طن متري (ton)  
- باوند (lb), أونصة (oz), ميكروغرام (µg)  

### **الحجم / السعة (Volume)**
- مليلتر (ml), لتر (l), متر مكعب (m3)  
- ملعقة صغيرة (tsp), ملعقة كبيرة (tbsp), كوب (cup)  
- باينت (pt), كوارتر (qt), جالون (gal), أونصة سائلة (fl_oz)  

### **الزمن (Time)**
- ثانية (s), دقيقة (min), ساعة (h), يوم (day), أسبوع (week), شهر (month), سنة (year)  

### **الحرارة (Temperature)**
- Celsius (C), Fahrenheit (F), Kelvin (K), Rankine (R)  

---

## 🔹 التثبيت
يمكنك نسخ الملفات مباشرة إلى مشروعك أو تحويلها إلى مكتبة قابلة للنشر.  

```bash


from unit_converter import (
    convert_length,
    convert_weight,
    convert_volume,
    convert_time,
    convert_temperature
)

# --------- الطول (Length) ---------
print("=== Length ===")
print("10 km =", convert_length(10, "km", "mile"), "mile")
print("12 inch =", convert_length(12, "inch", "cm"), "cm")
print("2 mile =", convert_length(2, "mile", "km"), "km")

# --------- الوزن / الكتلة (Weight) ---------
print("\n=== Weight ===")
print("5 kg =", convert_weight(5, "kg", "lb"), "lb")
print("16 oz =", convert_weight(16, "oz", "g"), "g")
print("1000 g =", convert_weight(1000, "g", "kg"), "kg")

# --------- الحجم / السعة (Volume) ---------
print("\n=== Volume ===")
print("3 l =", convert_volume(3, "l", "gal"), "gal")
print("2 cup =", convert_volume(2, "cup", "ml"), "ml")
print("1 m3 =", convert_volume(1, "m3", "l"), "l")

# --------- الزمن (Time) ---------
print("\n=== Time ===")
print("2 hours =", convert_time(2, "h", "min"), "minutes")
print("1 day =", convert_time(1, "day", "s"), "seconds")
print("3 week =", convert_time(3, "week", "day"), "days")

# --------- الحرارة (Temperature) ---------
print("\n=== Temperature ===")
print("100°C =", convert_temperature(100, "C", "F"), "°F")
print("0°C =", convert_temperature(0, "C", "K"), "K")
print("32°F =", convert_temperature(32, "F", "C"), "°C")


