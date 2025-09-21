from django.core.management.base import BaseCommand
from django.db import models
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class DjangoMGGenerator:
    FIELDS_CONFIG: Dict[str, Dict] = {
        "01": {"name": "name", "import": "", "field": "name = models.CharField(max_length=255)", "help": "Name", "pip": ""},
        "02": {"name": "title", "import": "", "field": "title = models.CharField(max_length=200)", "help": "Title", "pip": ""},
        "03": {"name": "slug", "import": "from autoslug import AutoSlugField", "field": "slug = AutoSlugField(populate_from='name', unique=True, max_length=255, blank=True)", "help": "Slug", "pip": "django-autoslug"},
        "04": {"name": "rich", "import": "from ckeditor.fields import RichTextField", "field": "description = RichTextField(blank=True, null=True)", "help": "Rich Text", "pip": "django-ckeditor"},
        "05": {"name": "text", "import": "", "field": "content = models.TextField(blank=True, null=True)", "help": "Text", "pip": ""},
        "06": {"name": "short", "import": "", "field": "short_description = models.CharField(max_length=500, blank=True, null=True)", "help": "Short Desc", "pip": ""},
        "07": {"name": "image", "import": "from filer.fields.image import FilerImageField", "field": "image = FilerImageField(null=True, blank=True, on_delete=models.SET_NULL)", "help": "Image", "pip": "django-filer"},
        "08": {"name": "gallery", "import": "", "field": "images = models.ManyToManyField('filer.Image', blank=True, related_name='%(class)s_images')", "help": "Gallery", "pip": "django-filer"},
        "09": {"name": "file", "import": "from filer.fields.file import FilerFileField", "field": "file = FilerFileField(null=True, blank=True, on_delete=models.SET_NULL)", "help": "File", "pip": "django-filer"},
        "10": {"name": "price", "import": "from djmoney.models.fields import MoneyField", "field": "price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')", "help": "Price", "pip": "django-money"},
        "11": {"name": "stock", "import": "", "field": "stock = models.PositiveIntegerField(default=0)", "help": "Stock", "pip": ""},
        "12": {"name": "active", "import": "", "field": "is_active = models.BooleanField(default=True)", "help": "Active", "pip": ""},
        "13": {"name": "sku", "import": "", "field": "sku = models.CharField(max_length=100, unique=True, blank=True, null=True)", "help": "SKU", "pip": ""},
        "14": {"name": "category", "import": "", "field": "category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='%(class)s_items')", "help": "Category", "pip": ""},
        "15": {"name": "tags", "import": "from taggit.managers import TaggableManager", "field": "tags = TaggableManager(blank=True)", "help": "Tags", "pip": "django-taggit"},
        "16": {"name": "author", "import": "from django.contrib.auth.models import User", "field": "created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created')", "help": "Author", "pip": ""},
        "17": {"name": "created", "import": "", "field": "created_at = models.DateTimeField(auto_now_add=True)", "help": "Created", "pip": ""},
        "18": {"name": "updated", "import": "", "field": "updated_at = models.DateTimeField(auto_now=True)", "help": "Updated", "pip": ""},
        "19": {"name": "published", "import": "", "field": "published_at = models.DateTimeField(null=True, blank=True)", "help": "Published", "pip": ""},
        "20": {"name": "weight", "import": "", "field": "weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)", "help": "Weight", "pip": ""},
        "21": {"name": "dimensions", "import": "", "field": "dimensions = models.CharField(max_length=50, blank=True, null=True)", "help": "Dimensions", "pip": ""},
        "22": {"name": "status", "import": "", "field": "status = models.CharField(max_length=20, choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')], default='draft')", "help": "Status", "pip": ""},
        "23": {"name": "priority", "import": "", "field": "priority = models.PositiveSmallIntegerField(default=0)", "help": "Priority", "pip": ""},
        "24": {"name": "meta", "import": "", "field": "meta_title = models.CharField(max_length=200, blank=True, null=True)", "help": "Meta Title", "pip": ""},
        "25": {"name": "desc", "import": "", "field": "meta_description = models.TextField(max_length=500, blank=True, null=True)", "help": "Meta Desc", "pip": ""},
        "26": {"name": "url", "import": "", "field": "url = models.URLField(blank=True, null=True)", "help": "URL", "pip": ""},
        "27": {"name": "email", "import": "", "field": "email = models.EmailField(blank=True, null=True)", "help": "Email", "pip": ""},
        "28": {"name": "phone", "import": "", "field": "phone = models.CharField(max_length=20, blank=True, null=True)", "help": "Phone", "pip": ""}
    }
    
    @classmethod
    def show_simple_guide(cls) -> str:
        guide = []
        guide.append("\n" + "=" * 70)
        guide.append("🚀 DJANGO-MG - MODEL GENERATOR")
        guide.append("   Created by Mobin Hasanghasemi")
        guide.append("   Email: mobin.hasanghasemi.m@gmail.com")
        guide.append("=" * 70)
        guide.append("")
        guide.append("📋 BASIC: 01=Name | 02=Title | 03=Slug")
        guide.append("📝 CONTENT: 04=Rich | 05=Text | 06=Short")
        guide.append("🖼️  MEDIA: 07=Image | 08=Gallery | 09=File")
        guide.append("💰 ECOM: 10=Price | 11=Stock | 12=Active | 13=SKU")
        guide.append("🔗 REL: 14=Category | 15=Tags | 16=Author")
        guide.append("⏰ TIME: 17=Created | 18=Updated | 19=Published")
        guide.append("⚙️  PRO: 20=Weight | 21=Dimensions | 22=Status | 23=Priority")
        guide.append("🔍 SEO: 24=Meta | 25=Desc")
        guide.append("📧 EXTRA: 26=URL | 27=Email | 28=Phone")
        guide.append("")
        guide.append("=" * 70)
        guide.append("💡 FORMAT: py filename.py ClassName 01/04/10/17")
        guide.append("   Example: py models.py Product 01/04/10/11/17")
        guide.append("   Means: Name + Rich + Price + Stock + Created")
        guide.append("=" * 70)
        return "\n".join(guide)
    
    @classmethod
    def validate_input(cls, user_input: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        parts = user_input.strip().split()
        if len(parts) < 3 or parts[0] != 'py':
            return None, None, None
        
        file_name = parts[1]
        class_name = parts[2]
        field_numbers = ""
        
        if len(parts) > 3:
            field_input = " ".join(parts[3:])
            field_numbers = "/".join([f for f in field_input.split("/") if f])
        
        if not file_name.endswith('.py'):
            file_name += '.py'
        
        if not class_name or not class_name[0].isupper():
            class_name = class_name.capitalize()
        
        field_codes = field_numbers.split('/')
        for code in field_codes:
            code = code.strip()
            if code and code not in cls.FIELDS_CONFIG:
                raise ValueError(f"Invalid field code: {code} (use 01-28)")
        
        return file_name, class_name, field_numbers
    
    @classmethod
    def generate_model(cls, file_name: str, class_name: str, field_numbers: str) -> Tuple[str, List[str]]:
        if not field_numbers:
            field_numbers = "01/17"
        
        field_codes = [code.strip() for code in field_numbers.split('/') if code.strip()]
        
        imports = ["from django.db import models"]
        pip_commands = []
        
        for code in field_codes:
            if code in cls.FIELDS_CONFIG:
                config = cls.FIELDS_CONFIG[code]
                if config["import"]:
                    imports.append(config["import"])
                if config["pip"]:
                    pip_commands.append(config["pip"])
        
        fields = []
        field_names = []
        for code in field_codes:
            if code in cls.FIELDS_CONFIG:
                config = cls.FIELDS_CONFIG[code]
                field_def = config['field'].replace('%(class)s', class_name.lower())
                fields.append(f"    {field_def}")
                field_names.append(config['name'])
        
        if "01" in field_codes:
            str_method = "    def __str__(self):\n        return self.name"
        elif "02" in field_codes:
            str_method = "    def __str__(self):\n        return self.title"
        else:
            str_method = "    def __str__(self):\n        return f'ID: {self.id}'"
        
        model_code = f"""# Auto-generated: {class_name}
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Fields: {', '.join(field_names)}
# Created by Mobin Hasanghasemi (mobin.hasanghasemi.m@gmail.com)

{chr(10).join(imports)}

class {class_name}(models.Model):
{chr(10).join(fields)}

{str_method}

    class Meta:
        verbose_name = '{class_name.lower()}'
        verbose_name_plural = '{class_name.lower()}s'
"""

        file_path = Path(file_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if f"class {class_name}" in content:
                return f"⚠️  Model '{class_name}' already exists!", []
            
            separator = "\n\n" + "="*60 + f"\n# New Model: {class_name}\n" + "="*60 + "\n\n"
            model_code = content + separator + model_code
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(model_code.strip() + "\n")
        
        return f"✅ Model '{class_name}' created! ({len(fields)} fields)", pip_commands

class Command(BaseCommand):
    help = '🚀 Django-MG: Slash Model Generator'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Django-MG Model Generator'))
        self.stdout.write('=' * 35)
        self.stdout.write(self.style.NOTICE('Created by Mobin Hasanghasemi'))
        self.stdout.write('Email: mobin.hasanghasemi.m@gmail.com')
        
        try:
            self.stdout.write("\n\n👋 Hi! Type 'generate.model' to start:")
            user_input = input(">>> ").strip()
            
            if user_input != "generate.model":
                self.stdout.write(self.style.ERROR("❌ Please type 'generate.model'"))
                return

            self.stdout.write("\n" + DjangoMGGenerator.show_simple_guide())
            
            self.stdout.write("\n🎯 Enter your command (e.g., py models.py Product 01/04/10/17):")
            user_input = input(">>> ").strip()
            
            try:
                file_name, class_name, field_numbers = DjangoMGGenerator.validate_input(user_input)
                if not file_name or not class_name:
                    raise ValueError("Invalid format!")
            except ValueError as e:
                self.stdout.write(self.style.ERROR(f"❌ {e}"))
                self.stdout.write(self.style.WARNING("💡 Example: py models.py Product 01/04/10/17"))
                return
            
            self.stdout.write(f"\n🔨 Creating '{class_name}' with fields: {field_numbers}")
            result, pip_commands = DjangoMGGenerator.generate_model(file_name, class_name, field_numbers)
            self.stdout.write(self.style.SUCCESS(result))
            
            if pip_commands:
                unique_pip = list(set(pip_commands))
                self.stdout.write(f"\n📦 Install packages:")
                self.stdout.write(f"   pip install {' '.join(unique_pip)}")
            else:
                self.stdout.write("\n📦 No additional packages needed!")
            
            field_codes = [code.strip() for code in field_numbers.split('/') if code.strip()]
            self.stdout.write(f"\n✅ Generated fields:")
            for code in field_codes:
                if code in DjangoMGGenerator.FIELDS_CONFIG:
                    field_name = DjangoMGGenerator.FIELDS_CONFIG[code]['help']
                    self.stdout.write(f"   • {field_name}")
            
            self.stdout.write(f"\n🚀 Next steps:")
            self.stdout.write("   python manage.py makemigrations")
            self.stdout.write("   python manage.py migrate")
            self.stdout.write(f"\n💡 Created by Mobin Hasanghasemi - mobin.hasanghasemi.m@gmail.com")
            
        except KeyboardInterrupt:
            self.stdout.write("\n\n👋 Cancelled by user")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"💥 Error: {str(e)}"))
            self.stdout.write(self.style.WARNING("💡 Contact: mobin.hasanghasemi.m@gmail.com"))