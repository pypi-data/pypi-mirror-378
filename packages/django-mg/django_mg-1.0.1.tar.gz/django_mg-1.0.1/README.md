# Django-MG 🔥

**Created by Mobin Hasanghasemi**  
*Email: mobin.hasanghasemi.m@gmail.com*

Django Model Generator. Slash-separated fields. Zero config.

## 🚀 Quick Start

### **Step 1: Install**
```bash
pip install django-mg
```

### **Step 2: Add to Django**
**`settings.py`:**
```python
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    
    # Add this
    'django_mg',  # Django-MG
]
```

### **Step 3: Generate Model**
```bash
python manage.py generate_model
```

### **Step 4: Follow Prompts**
```
👋 Hi! Type 'generate.model' to start:
>>> generate.model

🚀 DJANGO-MG - MODEL GENERATOR
Created by Mobin Hasanghasemi
Email: mobin.hasanghasemi.m@gmail.com
======================================================================
📋 BASIC: 01=Name | 02=Title | 03=Slug
📝 CONTENT: 04=Rich | 05=Text | 06=Short
🖼️  MEDIA: 07=Image | 08=Gallery | 09=File
💰 ECOM: 10=Price | 11=Stock | 12=Active | 13=SKU
🔗 REL: 14=Category | 15=Tags | 16=Author
⏰ TIME: 17=Created | 18=Updated | 19=Published
⚙️  PRO: 20=Weight | 21=Dimensions | 22=Status | 23=Priority
🔍 SEO: 24=Meta | 25=Desc
📧 EXTRA: 26=URL | 27=Email | 28=Phone
======================================================================
💡 FORMAT: py filename.py ClassName 01/04/10/17
   Example: py models.py Product 01/04/10/11/17
   Means: Name + Rich + Price + Stock + Created
======================================================================

🎯 Enter your command:
>>> py models.py Product 01/10/11/17

🔨 Creating 'Product' with fields: 01/10/11/17
✅ Model 'Product' created! (4 fields)

📦 Install packages:
   pip install django-money

✅ Generated fields:
   • Name
   • Price
   • Stock
   • Created

🚀 Next steps:
   python manage.py makemigrations
   python manage.py migrate
```

### **Step 5: Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 💡 **Field Codes Guide**

| Code | Field | Description | Package |
|------|-------|-------------|---------|
| `01` | **Name** | `CharField(max_length=255)` | - |
| `02` | **Title** | `CharField(max_length=200)` | - |
| `03` | **Slug** | Auto-slug from name | `django-autoslug` |
| `04` | **Rich** | RichTextField (CKEditor) | `django-ckeditor` |
| `05` | **Text** | `TextField()` | - |
| `06` | **Short** | `CharField(max_length=500)` | - |
| `07` | **Image** | FilerImageField | `django-filer` |
| `08` | **Gallery** | ManyToMany images | `django-filer` |
| `09` | **File** | FilerFileField | `django-filer` |
| `10` | **Price** | MoneyField (USD) | `django-money` |
| `11` | **Stock** | `PositiveIntegerField()` | - |
| `12` | **Active** | `BooleanField(default=True)` | - |
| `13` | **SKU** | `CharField(unique=True)` | - |
| `14` | **Category** | ForeignKey to Category | - |
| `15` | **Tags** | TaggableManager | `django-taggit` |
| `16` | **Author** | ForeignKey to User | - |
| `17` | **Created** | `DateTimeField(auto_now_add=True)` | - |
| `18` | **Updated** | `DateTimeField(auto_now=True)` | - |
| `19` | **Published** | `DateTimeField(null=True)` | - |
| `20` | **Weight** | `DecimalField(kg)` | - |
| `21` | **Dimensions** | `CharField(max_length=50)` | - |
| `22` | **Status** | Draft/Published/Archived | - |
| `23` | **Priority** | `PositiveSmallIntegerField()` | - |
| `24` | **Meta** | Meta title (SEO) | - |
| `25` | **Desc** | Meta description (SEO) | - |
| `26` | **URL** | `URLField()` | - |
| `27` | **Email** | `EmailField()` | - |
| `28` | **Phone** | `CharField(max_length=20)` | - |

---

## 💎 **Real Examples**

### **Product Model**
```bash
py models.py Product 01/10/11/12/17
```
**Fields:** Name + Price + Stock + Active + Created

### **Blog Post**
```bash
py blog/models.py Post 02/04/06/15/17/22
```
**Fields:** Title + Rich + Short + Tags + Created + Status

### **Image Gallery**
```bash
py gallery/models.py Photo 01/07/08/17
```
**Fields:** Name + Image + Gallery + Created

### **Contact Form**
```bash
py contact/models.py Contact 01/27/28/05/17
```
**Fields:** Name + Email + Phone + Text + Created

---

## 📦 **Optional Features**

### **Basic (No extras)**
```bash
pip install django-mg
```

### **E-commerce**
```bash
pip install "django-mg[money,filer]"
```

### **Content**
```bash
pip install "django-mg[ckeditor,taggit]"
```

### **Full Features**
```bash
pip install "django-mg[filer,money,ckeditor,taggit,autoslug]"
```

---

## 🛠️ **Troubleshooting**

### **"Unknown command: generate_model"**
```python
# settings.py
INSTALLED_APPS += ['django_mg']  # این خط رو اضافه کن
```

### **"Module not found"**
```bash
pip install django-mg  # دوباره نصب کن
```

### **"Invalid field code"**
```
# فقط 01-28 استفاده کن
# مثال: py models.py User 01/27/17  (Name + Email + Created)
```

### **Dependencies**
```bash
# pip requirements خودکار نشون میده
python manage.py generate_model
# 📦 Install packages:
#    pip install django-money
```

---

## 📊 **Generated Model Example**

**Command:** `py models.py Product 01/10/11/17`

**Output (`models.py`):**
```python
# Auto-generated: Product
# Generated: 2025-01-20 14:30:25
# Fields: name, price, stock, created
# Created by Mobin Hasanghasemi (mobin.hasanghasemi.m@gmail.com)

from django.db import models
from djmoney.models.fields import MoneyField

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'
```

---

## 🔗 **Links**

- **PyPI**: https://pypi.org/project/django-mg/

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file.

**© 2025 Mobin Hasanghasemi**  
📧 **mobin.hasanghasemi.m@gmail.com**

---
