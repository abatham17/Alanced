# Generated by Django 4.2.3 on 2023-08-05 16:34

from django.db import migrations, models
import django.db.models.deletion
import django_fields.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('features', models.CharField(default='', max_length=10000)),
                ('price', models.DecimalField(decimal_places=2, default='', max_digits=10)),
                ('duration', models.PositiveIntegerField(default='', help_text='Duration in days')),
                ('membership_type', models.CharField(choices=[('Freelancer', 'freelancer'), ('Hirer', 'hirer')], default='', max_length=100)),
            ],
            options={
                'db_table': 'Membership',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.TextField(default='')),
                ('rating', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='reviews_created', to='account.hirer')),
                ('created_for', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='reviews_received', to='account.freelancer')),
            ],
            options={
                'db_table': 'Review',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=200)),
                ('description', models.TextField(default='')),
                ('budget', models.DecimalField(decimal_places=2, default='', max_digits=10)),
                ('deadline', models.DateField(blank=True, null=True)),
                ('skills_required', models.CharField(default='', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.CharField(choices=[('Web_development', 'web_development'), ('Mobile_development', 'mobile_development'), ('Web_designing', 'web_designing'), ('Software_development', 'software_development'), ('Ui_Ux_designing', 'ui_ux_designing'), ('Logo_Designing', 'logo_Designing'), ('Graphics_designing', 'graphics_designing'), ('Cloud_computing', 'cloud_computing'), ('AI_ML', 'AI_ML'), ('Data_Science', 'data_Science')], default='', max_length=100)),
                ('project_owner', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='projects', to='account.hirer')),
            ],
            options={
                'db_table': 'Project',
            },
        ),
        migrations.CreateModel(
            name='FreelancerProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_title', models.CharField(default='', max_length=200)),
                ('project_description', models.TextField(default='')),
                ('project_link', models.URLField(default='')),
                ('images_logo', django_fields.fields.DefaultStaticImageField(blank=True, upload_to='images_logo')),
                ('project_pdf', models.FileField(default='images/default.pdf', upload_to='documents')),
                ('skills_used', models.CharField(default='', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.CharField(choices=[('Web_development', 'web_development'), ('Mobile_development', 'mobile_development'), ('Web_designing', 'web_designing'), ('Software_development', 'software_development'), ('Ui_Ux_designing', 'ui_ux_designing'), ('Logo_Designing', 'logo_Designing'), ('Graphics_designing', 'graphics_designing'), ('Cloud_computing', 'cloud_computing'), ('AI_ML', 'AI_ML'), ('Data_Science', 'data_Science')], default='', max_length=100)),
                ('design_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='selfprojects', to='account.freelancer')),
            ],
            options={
                'db_table': 'FreelancerProject',
            },
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField(default='')),
                ('bid_time', models.DateTimeField(auto_now_add=True)),
                ('freelancer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='bid', to='account.freelancer')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='bid', to='FreelanceTask.project')),
            ],
            options={
                'db_table': 'Bid',
            },
        ),
    ]
