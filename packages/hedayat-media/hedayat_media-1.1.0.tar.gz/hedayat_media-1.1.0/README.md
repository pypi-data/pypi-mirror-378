# HedayatMedia 📖✨

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

کتابخانه **HedayatMedia** ابزاری جامع برای کار با داده‌های اسلامی است:  
- 📜 احادیث  
- 📖 قرآن (آیات، سوره‌ها، اجزاء)  
- 🕋 اذکار روزانه  
- 🌍 مکان‌یابی مساجد  


---
# نمونه ها
```python
from hedayat_media import HedayatMedia

# نمونه‌سازی
media = HedayatMedia()

# دریافت یک حدیث تصادفی
print(media.get_random_hadith())

# دریافت یک آیه تصادفی
print(media.get_random_ayah())

# دریافت ذکر روز
print(media.get_zeker())


hadith = media.get_random_hadith()
print(hadith["text_arabic"])

# آیه تصادفی از جزء 5
ayah = media.fetch_random_ayah(juz_number=5)
print(ayah)

# کل سوره بقره
surah = media.get_surah(2)
print(surah["name_ar"], surah["number_of_ayahs"])


print(media.get_zeker())

lat, lon = media.get_coordinates("Mashhad")
bbox = media.get_bounding_box(lat, lon, radius_km=5)
data = media.get_overpass_data(bbox)
mosques = media.process_data(data)

for m in mosques:
    print(m["name"], m["map_link"])






```



---
# 📖 API Reference
HedayatMedia.load_hadiths()

بارگذاری احادیث از فایل JSON.

HedayatMedia.get_random_hadith()

یک حدیث تصادفی برمی‌گرداند.

HedayatMedia.fetch_random_ayah(juz_number: int)

آیه تصادفی از یک جزء مشخص.

HedayatMedia.get_random_ayah()

آیه تصادفی از کل قرآن.

HedayatMedia.get_all_surahs()

لیست همه سوره‌ها.

HedayatMedia.get_surah(surah_number: int)

جزئیات یک سوره شامل متن و صوت.

HedayatMedia.get_zeker()

ذکر روز هفته.

HedayatMedia.get_coordinates(place_name: str)

مختصات یک مکان (شهر/محله).

HedayatMedia.get_bounding_box(lat, lon, radius_km=10)

ایجاد محدوده جغرافیایی برای جستجو.

HedayatMedia.get_overpass_data(bbox)

دریافت داده مساجد از Overpass API.

HedayatMedia.process_data(data)

پردازش داده API و برگرداندن لیست مساجد.


--- 
# نمونه کد کامل از تمامی متد های کتابخانه
```python
from hedayat_media import HedayatMedia

def main():
    media = HedayatMedia()

    print("📜 حدیث تصادفی:")
    print(media.get_random_hadith())
    print("="*60)

    print("📖 آیه تصادفی از کل قرآن:")
    print(media.get_random_ayah())
    print("="*60)

    print("📖 آیه تصادفی از جزء 5:")
    print(media.fetch_random_ayah(juz_number=5))
    print("="*60)

    print("📖 لیست همه سوره‌ها (فقط چندتا):")
    surahs = media.get_all_surahs()
    if isinstance(surahs, list):
        for s in surahs[:5]:
            print(f"{s['number']}. {s['englishName']} ({s['name']})")
    print("="*60)

    print("📖 دریافت سوره بقره:")
    surah = media.get_surah(2)
    print(f"{surah['name_ar']} - تعداد آیات: {surah['number_of_ayahs']}")
    print("="*60)

    print("🕋 ذکر امروز:")
    print(media.get_zeker())
    print("="*60)

    print("🌍 جغرافیا (مساجد مشهد):")
    coords = media.get_coordinates("Mashhad")
    if coords:
        lat, lon = coords
        bbox = media.get_bounding_box(lat, lon, radius_km=2)
        mosques_data = media.get_overpass_data(bbox)
        mosques = media.process_data(mosques_data)
        for m in mosques[:3]:
            print(f"{m['name']} → {m['map_link']}")
    print("="*60)

if __name__ == "__main__":
    main()

```

## 📦 نصب

```bash
pip install hedayat_media







