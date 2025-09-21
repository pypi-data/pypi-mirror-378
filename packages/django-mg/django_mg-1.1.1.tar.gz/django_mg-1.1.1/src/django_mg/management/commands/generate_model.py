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
    "03": {"name": "slug", "import": "", "field": "slug = models.SlugField(unique=True, max_length=255)", "help": "Slug", "pip": ""},
    "04": {"name": "uuid", "import": "from django_extensions.db.fields import UUIDField", "field": "uuid = UUIDField(auto=True)", "help": "UUID", "pip": "django-extensions"},
    "05": {"name": "autoslug", "import": "from autoslug import AutoSlugField", "field": "slug = AutoSlugField(populate_from='name', unique=True, max_length=255, blank=True)", "help": "Auto Slug", "pip": "django-autoslug"},
    "06": {"name": "shortuuid", "import": "from shortuuidfield import ShortUUIDField", "field": "uid = ShortUUIDField()", "help": "Short UUID", "pip": "shortuuidfield"},
    "07": {"name": "text", "import": "", "field": "content = models.TextField(blank=True, null=True)", "help": "Text", "pip": ""},
    "08": {"name": "short_text", "import": "", "field": "short_description = models.CharField(max_length=500, blank=True, null=True)", "help": "Short Text", "pip": ""},
    "09": {"name": "integer", "import": "", "field": "number = models.IntegerField()", "help": "Integer", "pip": ""},
    "10": {"name": "positive_integer", "import": "", "field": "count = models.PositiveIntegerField()", "help": "Positive Integer", "pip": ""},
    "11": {"name": "small_integer", "import": "", "field": "value = models.SmallIntegerField()", "help": "Small Integer", "pip": ""},
    "12": {"name": "positive_small_integer", "import": "", "field": "small_count = models.PositiveSmallIntegerField()", "help": "Positive Small Integer", "pip": ""},
    "13": {"name": "big_integer", "import": "", "field": "big_number = models.BigIntegerField()", "help": "Big Integer", "pip": ""},
    "14": {"name": "decimal", "import": "", "field": "amount = models.DecimalField(max_digits=12, decimal_places=2)", "help": "Decimal", "pip": ""},
    "15": {"name": "float", "import": "", "field": "rate = models.FloatField()", "help": "Float", "pip": ""},
    "16": {"name": "money", "import": "from djmoney.models.fields import MoneyField", "field": "price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')", "help": "Money", "pip": "django-money"},
    "17": {"name": "date", "import": "", "field": "date = models.DateField()", "help": "Date", "pip": ""},
    "18": {"name": "datetime", "import": "", "field": "created_at = models.DateTimeField(auto_now_add=True)", "help": "DateTime", "pip": ""},
    "19": {"name": "time", "import": "", "field": "time = models.TimeField()", "help": "Time", "pip": ""},
    "20": {"name": "duration", "import": "", "field": "duration = models.DurationField()", "help": "Duration", "pip": ""},
    "21": {"name": "monitor", "import": "from model_utils.fields import MonitorField", "field": "monitored = MonitorField(monitor='status')", "help": "Monitor Field", "pip": "django-model-utils"},

    "22": {"name": "auto_created", "import": "from model_utils.fields import AutoCreatedField", "field": "created = AutoCreatedField()", "help": "Auto Created", "pip": "django-model-utils"},
    "23": {"name": "auto_modified", "import": "from model_utils.fields import AutoLastModifiedField", "field": "modified = AutoLastModifiedField()", "help": "Auto Modified", "pip": "django-model-utils"},
    "24": {"name": "boolean", "import": "", "field": "is_active = models.BooleanField(default=True)", "help": "Boolean", "pip": ""},
    "25": {"name": "null_boolean", "import": "", "field": "flag = models.BooleanField(null=True)", "help": "Null Boolean", "pip": ""},
    "26": {"name": "status_field", "import": "from model_utils.fields import StatusField", "field": "status = StatusField()", "help": "Status Field", "pip": "django-model-utils"},
    "27": {"name": "fsm_field", "import": "from django_fsm import FSMField", "field": "state = FSMField(default='new')", "help": "Finite State Machine Field", "pip": "django-fsm"},
    "28": {"name": "email", "import": "", "field": "email = models.EmailField(blank=True, null=True)", "help": "Email", "pip": ""},
    "29": {"name": "url", "import": "", "field": "url = models.URLField(blank=True, null=True)", "help": "URL", "pip": ""},
    "30": {"name": "ip_address", "import": "", "field": "ip = models.GenericIPAddressField(blank=True, null=True)", "help": "IP Address", "pip": ""},
    "31": {"name": "phone", "import": "from phonenumber_field.modelfields import PhoneNumberField", "field": "phone = PhoneNumberField(blank=True, null=True)", "help": "Phone Number", "pip": "django-phonenumber-field"},
    "32": {"name": "country", "import": "from django_countries.fields import CountryField", "field": "country = CountryField(blank_label='(select country)')", "help": "Country", "pip": "django-countries"},
    "33": {"name": "region", "import": "from django_countries_plus.fields import RegionField", "field": "region = RegionField(blank=True, null=True)", "help": "Region", "pip": "django-countries-plus"},
    "34": {"name": "file", "import": "", "field": "file = models.FileField(upload_to='files/', blank=True, null=True)", "help": "File", "pip": ""},
    "35": {"name": "image", "import": "", "field": "image = models.ImageField(upload_to='images/', blank=True, null=True)", "help": "Image", "pip": ""},
    "36": {"name": "thumbnail_image", "import": "from easy_thumbnails.fields import ThumbnailerImageField", "field": "thumbnail = ThumbnailerImageField(upload_to='thumbnails/', blank=True, null=True)", "help": "Thumbnail Image", "pip": "easy-thumbnails"},
    "37": {"name": "processed_image", "import": "from imagekit.models import ProcessedImageField", "field": "processed_image = ProcessedImageField(upload_to='processed/', blank=True, null=True)", "help": "Processed Image", "pip": "django-imagekit"},
    "38": {"name": "filer_file", "import": "from filer.fields.file import FilerFileField", "field": "file = FilerFileField(null=True, blank=True, on_delete=models.SET_NULL)", "help": "Filer File", "pip": "django-filer"},
    "39": {"name": "filer_image", "import": "from filer.fields.image import FilerImageField", "field": "image = FilerImageField(null=True, blank=True, on_delete=models.SET_NULL)", "help": "Filer Image", "pip": "django-filer"},
    "40": {"name": "rich_text", "import": "from ckeditor.fields import RichTextField", "field": "description = RichTextField(blank=True, null=True)", "help": "Rich Text", "pip": "django-ckeditor"},
    "41": {"name": "quill", "import": "from django_quill.fields import QuillField", "field": "content = QuillField(blank=True, null=True)", "help": "Quill Rich Text", "pip": "django-quill-editor"},
    "42": {"name": "markdown", "import": "from markdownx.models import MarkdownxField", "field": "content = MarkdownxField(blank=True, null=True)", "help": "Markdown Text", "pip": "django-markdownx"},
    "43": {"name": "redactor", "import": "from redactor.fields import RedactorField", "field": "content = RedactorField(blank=True, null=True)", "help": "Redactor Rich Text", "pip": "django-redactor"},
    "44": {"name": "tags", "import": "from taggit.managers import TaggableManager", "field": "tags = TaggableManager(blank=True)", "help": "Tags", "pip": "django-taggit"},
    "45": {"name": "array_field", "import": "from django.contrib.postgres.fields import ArrayField", "field": "array_data = ArrayField(models.CharField(max_length=100), blank=True, null=True)", "help": "Array Field", "pip": ""},
    "46": {"name": "json_field", "import": "from django.contrib.postgres.fields import JSONField", "field": "data = JSONField(blank=True, null=True)", "help": "JSON Field", "pip": ""},
    "47": {"name": "hstore_field", "import": "from django.contrib.postgres.fields import HStoreField", "field": "hstore_data = HStoreField(blank=True, null=True)", "help": "HStore Field", "pip": ""},
    "48": {"name": "pickled_object", "import": "from picklefield.fields import PickledObjectField", "field": "obj = PickledObjectField(blank=True, null=True)", "help": "Pickled Object", "pip": "django-picklefield"},
    "49": {"name": "encrypted_char", "import": "from encrypted_model_fields.fields import EncryptedCharField", "field": "secret_text = EncryptedCharField(max_length=255, blank=True, null=True)", "help": "Encrypted Char", "pip": "django-encrypted-model-fields"},
    "50": {"name": "encrypted_text", "import": "from encrypted_model_fields.fields import EncryptedTextField", "field": "secret_content = EncryptedTextField(blank=True, null=True)", "help": "Encrypted Text", "pip": "django-encrypted-model-fields"},
    "51": {"name": "one_to_one_user", "import": "from django.contrib.auth.models import User", "field": "user = models.OneToOneField(User, on_delete=models.CASCADE)", "help": "OneToOne User", "pip": ""},
    "52": {"name": "foreign_key_user", "import": "from django.contrib.auth.models import User", "field": "user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)", "help": "ForeignKey User", "pip": ""},
    "53": {"name": "foreign_key", "import": "", "field": "fk = models.ForeignKey('OtherModel', on_delete=models.CASCADE)", "help": "ForeignKey", "pip": ""},
    "54": {"name": "one_to_one", "import": "", "field": "o2o = models.OneToOneField('OtherModel', on_delete=models.CASCADE)", "help": "OneToOne", "pip": ""},
    "55": {"name": "many_to_many", "import": "", "field": "m2m = models.ManyToManyField('OtherModel', blank=True)", "help": "ManyToMany", "pip": ""},
    "56": {"name": "generic_foreign_key", "import": "from django.contrib.contenttypes.fields import GenericForeignKey", "field": "content_object = GenericForeignKey()", "help": "Generic Foreign Key", "pip": ""},
    "57": {"name": "generic_relation", "import": "from django.contrib.contenttypes.fields import GenericRelation", "field": "related_objects = GenericRelation('OtherModel')", "help": "Generic Relation", "pip": ""},
    "58": {"name": "point", "import": "from django.contrib.gis.db.models import PointField", "field": "location = PointField(blank=True, null=True)", "help": "Point Field", "pip": "django.contrib.gis"},
    "59": {"name": "polygon", "import": "from django.contrib.gis.db.models import PolygonField", "field": "area = PolygonField(blank=True, null=True)", "help": "Polygon Field", "pip": "django.contrib.gis"},
    "60": {"name": "line_string", "import": "from django.contrib.gis.db.models import LineStringField", "field": "path = LineStringField(blank=True, null=True)", "help": "LineString Field", "pip": "django.contrib.gis"},
    "61": {"name": "country_field", "import": "from django_countries.fields import CountryField", "field": "country = CountryField(blank_label='(select country)')", "help": "Country Field", "pip": "django-countries"},
    "62": {"name": "address", "import": "from django_address.models import AddressField", "field": "address = AddressField(blank=True, null=True)", "help": "Address Field", "pip": "django-address"},
    "63": {"name": "location_field", "import": "from location_field.models.plain import PlainLocationField", "field": "location = PlainLocationField(based_fields=['city'], zoom=7)", "help": "Location Field", "pip": "django-location-field"},
    "64": {"name": "money_field", "import": "from djmoney.models.fields import MoneyField", "field": "price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')", "help": "Money Field", "pip": "django-money"},
    "65": {"name": "currency_field", "import": "from djmoney.models.fields import CurrencyField", "field": "currency = CurrencyField(default='USD')", "help": "Currency Field", "pip": "django-money"},
    "66": {"name": "decimal_price", "import": "", "field": "price = models.DecimalField(max_digits=14, decimal_places=2)", "help": "Decimal Price", "pip": ""},
    "67": {"name": "positive_stock", "import": "", "field": "stock = models.PositiveIntegerField(default=0)", "help": "Stock Quantity", "pip": ""},
    "68": {"name": "tax_field", "import": "", "field": "tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)", "help": "Tax Field", "pip": ""},
    "69": {"name": "color_field", "import": "from colorfield.fields import ColorField", "field": "color = ColorField(default='#FFFFFF')", "help": "Color Field", "pip": "django-colorfield"},
    "70": {"name": "json_field_api", "import": "from django.contrib.postgres.fields import JSONField", "field": "data = JSONField(blank=True, null=True)", "help": "JSON API Field", "pip": ""},
    "71": {"name": "encrypted_datetime", "import": "from encrypted_model_fields.fields import EncryptedDateTimeField", "field": "secret_date = EncryptedDateTimeField(blank=True, null=True)", "help": "Encrypted DateTime", "pip": "django-encrypted-model-fields"},
    "72": {"name": "ip_address2", "import": "", "field": "ip_address = models.GenericIPAddressField(blank=True, null=True)", "help": "IP Address", "pip": ""},
    "73": {"name": "mac_address", "import": "from django.db.models import MACAddressField", "field": "mac = MACAddressField(blank=True, null=True)", "help": "MAC Address", "pip": ""},
    "74": {"name": "language_field", "import": "from django_language_field.models import LanguageField", "field": "language = LanguageField(blank=True, null=True)", "help": "Language Field", "pip": "django-language-field"},
    "75": {"name": "country_multiple", "import": "from django_countries.fields import CountryField", "field": "countries = CountryField(multiple=True)", "help": "Multiple Countries", "pip": "django-countries"},
    "76": {"name": "historical_records", "import": "from simple_history.models import HistoricalRecords", "field": "history = HistoricalRecords()", "help": "Historical Records", "pip": "django-simple-history"},
    "77": {"name": "audit_log", "import": "from auditlog.registry import auditlog", "field": "auditlog.register('self')", "help": "Audit Log", "pip": "django-auditlog"},
    "78": {"name": "reversion", "import": "import reversion", "field": "reversion.register('self')", "help": "Versioning (Reversion)", "pip": "django-reversion"},
    "79": {"name": "status_meta", "import": "from model_utils.fields import StatusField", "field": "status = StatusField()", "help": "Status Meta Field", "pip": "django-model-utils"},
    "80": {"name": "monitor_meta", "import": "from model_utils.fields import MonitorField", "field": "monitor = MonitorField(monitor='status')", "help": "Monitor Meta Field", "pip": "django-model-utils"},
    "81": {"name": "ci_char", "import": "from citext.fields import CICharField", "field": "ci_text = CICharField(max_length=255)", "help": "Case-Insensitive Char", "pip": "django-citext"},
    "82": {"name": "ci_null_char", "import": "from citext.fields import CINullCharField", "field": "ci_text_null = CINullCharField(max_length=255, blank=True, null=True)", "help": "Case-Insensitive Null Char", "pip": "django-citext"},
    "83": {"name": "json_api", "import": "from django.contrib.postgres.fields import JSONField", "field": "api_data = JSONField(blank=True, null=True)", "help": "JSON API Data", "pip": ""},
    "84": {"name": "first_name", "import": "", "field": "first_name = models.CharField(max_length=100, blank=True, null=True)", "help": "First Name", "pip": ""},
    "85": {"name": "last_name", "import": "", "field": "last_name = models.CharField(max_length=100, blank=True, null=True)", "help": "Last Name", "pip": ""},
    "86": {"name": "username", "import": "", "field": "username = models.CharField(max_length=150, unique=True)", "help": "Username", "pip": ""},
    "87": {"name": "bio", "import": "", "field": "bio = models.TextField(blank=True, null=True)", "help": "Bio", "pip": ""},
    "88": {"name": "avatar", "import": "", "field": "avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)", "help": "Avatar", "pip": ""},
    "89": {"name": "cover_image", "import": "", "field": "cover = models.ImageField(upload_to='covers/', blank=True, null=True)", "help": "Cover Image", "pip": ""},
    "90": {"name": "birth_date", "import": "", "field": "birth_date = models.DateField(blank=True, null=True)", "help": "Birth Date", "pip": ""},
    "91": {"name": "gender", "import": "", "field": "gender = models.CharField(max_length=10, choices=[('male','Male'),('female','Female'),('other','Other')], blank=True, null=True)", "help": "Gender", "pip": ""},
    "92": {"name": "language_pref", "import": "", "field": "language_pref = models.CharField(max_length=20, blank=True, null=True)", "help": "Language Preference", "pip": ""},
    "93": {"name": "timezone_field", "import": "from timezone_field import TimeZoneField", "field": "timezone = TimeZoneField(default='UTC')", "help": "Timezone Field", "pip": "django-timezone-field"},
    "94": {"name": "subscription_status", "import": "", "field": "subscription_status = models.CharField(max_length=20, choices=[('free','Free'),('paid','Paid')], default='free')", "help": "Subscription Status", "pip": ""},
    "95": {"name": "notification_pref", "import": "from django.contrib.postgres.fields import JSONField", "field": "notification_pref = JSONField(blank=True, null=True)", "help": "Notification Preference", "pip": ""},
    "96": {"name": "agreement_accepted", "import": "", "field": "agreement_accepted = models.BooleanField(default=False)", "help": "Agreement Accepted", "pip": ""},
    "97": {"name": "terms_version", "import": "", "field": "terms_version = models.CharField(max_length=50, blank=True, null=True)", "help": "Terms Version", "pip": ""},
    "98": {"name": "last_login_ip", "import": "", "field": "last_login_ip = models.GenericIPAddressField(blank=True, null=True)", "help": "Last Login IP", "pip": ""},
    "99": {"name": "last_seen", "import": "", "field": "last_seen = models.DateTimeField(blank=True, null=True)", "help": "Last Seen DateTime", "pip": ""},
    "100": {"name": "activity_log", "import": "from django.contrib.postgres.fields import JSONField", "field": "activity_log = JSONField(blank=True, null=True)", "help": "Activity Log", "pip": ""}


    }
    # ------------------------------------------------------------------
    # 1) راهنمای جدید (کدهای ۰۱ تا ۱۰۰)
    # ------------------------------------------------------------------
    @classmethod
    def show_simple_guide(cls) -> str:
        guide = []
        guide.append("\n" + "=" * 70)
        guide.append("🚀 DJANGO-MG - MODEL GENERATOR")
        guide.append("   Created by Mobin Hasanghasemi")
        guide.append("   Email: mobin.hasanghasemi.m@gmail.com")
        guide.append("=" * 70)
        guide.append("")
        guide.append("📋 BASIC:        01=Name  02=Title  03=Slug  84=FirstName  85=LastName  86=Username")
        guide.append("📝 CONTENT:      07=Text  08=ShortText  40=RichText  41=Quill  42=Markdown  87=Bio")
        guide.append("🖼️  MEDIA:       34=File  35=Image  36=Thumb  37=Processed  38=FilerFile  39=FilerImage")
        guide.append("💰 ECOM:         14=Decimal  15=Float  16=Money  66=Price  67=Stock  68=Tax")
        guide.append("🔗 RELATIONS:    51=O2O-User  52=FK-User  53=FK  54=O2O  55=M2M  56=GFK  57=GR")
        guide.append("⏰ TIME:         17=Date  18=DateTime  19=Time  20=Duration  90=BirthDate  99=LastSeen")
        guide.append("⚙️  FLAGS:       24=Bool  25=NullBool  94=Status  96=Agreement  98=LastIP")
        guide.append("🔍 SEO / META:   03=Slug  26=StatusMeta  79=StatusMeta  80=MonitorMeta")
        guide.append("📧 CONTACT:      28=Email  29=URL  30=IP  31=Phone")
        guide.append("🌍 LOCATION:     32=Country  61=Country  75=MultiCountry  62=Address  63=Location")
        guide.append("🗺️  GIS:         58=Point  59=Polygon  60=LineString")
        guide.append("🔐 SECURITY:     49=EncChar  50=EncText  71=EncDateTime")
        guide.append("🧩 ADVANCED:     44=Tags  45=Array  46=JSON  47=HStore  48=Pickle  70=JSON_API  83=JSON_API")
        guide.append("📜 HISTORY:      76=History  77=AuditLog  78=Reversion")
        guide.append("🌐 INTL:         74=Language  93=Timezone")
        guide.append("🎨 UI:           69=Color")
        guide.append("🧪 POSTGRES:     81=CIChar  82=CINullChar")
        guide.append("")
        guide.append("=" * 70)
        guide.append("💡 FORMAT: py filename.py ClassName 01/04/10/17")
        guide.append("   Example: py models.py Product 01/07/16/35/67/18")
        guide.append("   Means: Name + Text + Money + Image + Stock + Created")
        guide.append("=" * 70)
        return "\n".join(guide)

    # ------------------------------------------------------------------
    # 2) اعتبارسنجی ورودی (محدوده ۰۱–۱۰۰)
    # ------------------------------------------------------------------
    @classmethod
    def validate_input(cls, user_input: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        parts = user_input.strip().split()
        if len(parts) < 3 or parts[0] != 'py':
            return None, None, None

        file_name = parts[1]
        class_name = parts[2]
        field_numbers = "/".join([f for f in parts[3:] if f])

        if not file_name.endswith('.py'):
            file_name += '.py'

        class_name = class_name.capitalize() if class_name else ""

        # بررسی معتبر بودن کدها
        for code in field_numbers.split('/'):
            code = code.strip()
            if code and code not in cls.FIELDS_CONFIG:
                raise ValueError(f"Invalid field code: {code} (use 01-100)")

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