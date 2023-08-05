# Generated by Django 4.2.3 on 2023-08-05 16:34

import django.core.validators
from django.db import migrations, models
import django_fields.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('date_of_creation', models.DateField(auto_now_add=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('images_logo', django_fields.fields.DefaultStaticImageField(blank=True, upload_to='images_logo')),
                ('type', models.CharField(choices=[('OWNER', 'owner'), ('HIRER', 'hirer'), ('FREELANCER', 'freelancer')], default='OWNER', max_length=20)),
                ('email', models.EmailField(max_length=200, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_hirer', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('Company_Name', models.CharField(default='', max_length=50)),
                ('is_freelancer', models.BooleanField(default=False)),
                ('is_owner', models.BooleanField(default=False)),
                ('first_Name', models.CharField(default='', max_length=25)),
                ('last_Name', models.CharField(default='', max_length=25)),
                ('experience', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(99)])),
                ('qualification', models.TextField(default='')),
                ('contact', models.CharField(max_length=10)),
                ('about', models.TextField(default='')),
                ('Company_Establish', models.DateField(blank=True, null=True)),
                ('skills', models.TextField(default='')),
                ('social_media', models.URLField(default='')),
                ('Block', models.BooleanField(default=False)),
                ('map', models.URLField(default='')),
                ('Address', models.TextField(default='')),
                ('DOB', models.DateField(blank=True, null=True)),
                ('category', models.CharField(choices=[('Web_development', 'web_development'), ('Mobile_development', 'mobile_development'), ('Web_designing', 'web_designing'), ('Software_development', 'software_development'), ('Ui_Ux_designing', 'ui_ux_designing'), ('Logo_Designing', 'logo_Designing'), ('Graphics_designing', 'graphics_designing'), ('Cloud_computing', 'cloud_computing'), ('AI_ML', 'AI_ML'), ('Data_Science', 'data_Science')], default='', max_length=100)),
                ('gender', models.CharField(choices=[('Male', 'male'), ('Female', 'female')], default='Male', max_length=8)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Freelancer',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('account.useraccount',),
        ),
        migrations.CreateModel(
            name='Hirer',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('account.useraccount',),
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('account.useraccount',),
        ),
    ]
