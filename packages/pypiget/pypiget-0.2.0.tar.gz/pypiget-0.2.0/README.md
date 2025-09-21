
# PyPi Python Library

یک کتابخانه پایتون برای دریافت اطلاعات پکیج‌های PyPI به صورت **سینک** یا **آسنکرون**.  
این کتابخانه به طور خودکار تشخیص می‌دهد که در محیط آسنکرون هستید یا نه و متد مناسب را استفاده می‌کند.

---

## نصب

برای نصب نیازی به پکیج خاصی نیست جز `requests` و `aiohttp`:

```bash
pip install requests aiohttp pypiget
```

سپس فایل `pypi.py` را در پروژه خود قرار دهید و import کنید:

```python
from pypi import PyPi
```

---

## استفاده

### نمونه سینک:

```python
from pypi import PyPi

pypi = PyPi()

# اطلاعات پکیج
info = pypi.get_package_info("requests")
print(info)

# ورژن‌های پکیج
releases = pypi.get_releases("requests")
print(releases)

# بررسی به‌روزرسانی
is_updated = pypi.is_package_updated("requests")
print(is_updated)

# اطلاعات نویسنده
author_info = pypi.show_package_author_info("requests")
print(author_info)

# تاریخ آخرین آپدیت
last_update = pypi.show_last_update_date("requests")
print(last_update)

# URL صفحه اصلی پکیج
home_url = pypi.get_package_url("requests")
print(home_url)
```

### نمونه آسنکرون:

```python
import asyncio
from pypi import PyPi

async def main():
    pypi = PyPi()

    # اطلاعات پکیج
    info = await pypi.get_package_info("requests")
    print(info)

    # بررسی وضعیت پکیج
    status = await pypi.check_package_status("requests")
    print(status)

asyncio.run(main())
```

---

## متدها

| متد | توضیح | نوع |
| --- | --- | --- |
| `get_package_info(package_name)` | دریافت اطلاعات کامل پکیج | سینک/آسنکرون |
| `get_releases(package_name)` | دریافت لیست ورژن‌ها | سینک/آسنکرون |
| `is_package_updated(package_name)` | بررسی آخرین به‌روزرسانی (<30 روز) | سینک/آسنکرون |
| `show_package_author_info(package_name)` | اطلاعات نویسنده (نام و ایمیل) | سینک/آسنکرون |
| `show_last_update_date(package_name)` | تاریخ آخرین آپدیت | سینک/آسنکرون |
| `get_popular_packages(limit=10)` | دریافت لیست پکیج‌های محبوب (HTML) | سینک/آسنکرون |
| `get_package_url(package_name)` | URL صفحه خانه پکیج | سینک/آسنکرون |
| `get_first_release_date(package_name)` | تاریخ اولین انتشار پکیج | سینک/آسنکرون |
| `check_package_status(package_name)` | بررسی موجودیت پکیج | سینک/آسنکرون |

---

## ویژگی‌ها

- خودکار تشخیص محیط سینک یا آسنکرون
- پشتیبانی کامل از تمام متدهای PyPI
- طراحی ساده و یکپارچه
- امکان استفاده در پروژه‌های async بدون تغییر کد

---

## مثال پیشرفته

می‌توان از متدها در پروژه‌های ترکیبی استفاده کرد، بدون اینکه نگران محیط سینک یا async باشید:

```python
import asyncio
from pypi import PyPi

pypi = PyPi()

async def main():
    info = await pypi.get_package_info("requests")
    print(info['info']['summary'])

asyncio.run(main())

# یا سینک مستقیم
releases = pypi.get_releases("requests")
print(releases)
```

---

## نصب در پروژه

کافیست فایل `pypi.py` را در پروژه خود قرار دهید و import کنید:

```
project/
├─ main.py
├─ pypi.py
└─ ...
```

---

## مجوز

MIT License  
می‌توانید آزادانه استفاده، تغییر و انتشار دهید.
