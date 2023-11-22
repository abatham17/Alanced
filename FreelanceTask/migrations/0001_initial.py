# Generated by Django 4.2.3 on 2023-11-22 15:17

from decimal import Decimal
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
                ('price', models.DecimalField(decimal_places=2, default='', max_digits=6)),
                ('duration', models.PositiveIntegerField(default='', help_text='Duration in days')),
                ('membership_type', models.CharField(choices=[('Freelancer', 'freelancer'), ('Hirer', 'hirer')], default='', max_length=50)),
            ],
            options={
                'db_table': 'Membership',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=200)),
                ('description', models.TextField(default='')),
                ('deadline', models.DateField(blank=True, null=True)),
                ('skills_required', models.CharField(default='', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.TextField(default='')),
                ('rate', models.CharField(choices=[('Hourly', 'hourly'), ('Fixed', 'fixed')], default='', max_length=15)),
                ('min_hourly_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, null=True)),
                ('max_hourly_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, null=True)),
                ('fixed_budget', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('experience_level', models.CharField(choices=[('Entry_Level', 'entry_Level'), ('Intermediate', 'intermediate'), ('Expert', 'expert')], default='', max_length=50)),
                ('is_hired', models.BooleanField(default=False)),
                ('project_owner', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='projects', to='account.hirer')),
            ],
            options={
                'db_table': 'Project',
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=200, unique=True)),
                ('subscribed_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'Subscription',
            },
        ),
        migrations.CreateModel(
            name='UserContactUs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Applicant_Email', models.EmailField(max_length=200, unique=True)),
                ('Applicant_Name', models.CharField(default='', max_length=25)),
                ('Applicant_Contact', models.CharField(default='', max_length=10)),
                ('Message', models.TextField(default='')),
            ],
            options={
                'db_table': 'UserContactUs',
            },
        ),
        migrations.CreateModel(
            name='SavedProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_saved', models.DateTimeField(auto_now_add=True)),
                ('freelancer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='saved_jobs', to='account.freelancer')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='saved_projects', to='FreelanceTask.project')),
            ],
            options={
                'db_table': 'SavedProject',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.TextField(default='')),
                ('rating', models.DecimalField(choices=[(Decimal('1.0'), Decimal('1.0')), (Decimal('1.5'), Decimal('1.5')), (Decimal('2.0'), Decimal('2.0')), (Decimal('2.5'), Decimal('2.5')), (Decimal('3.0'), Decimal('3.0')), (Decimal('3.5'), Decimal('3.5')), (Decimal('4.0'), Decimal('4.0')), (Decimal('4.5'), Decimal('4.5')), (Decimal('5.0'), Decimal('5.0'))], decimal_places=1, default=Decimal('1.0'), max_digits=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='reviews_created', to='account.hirer')),
                ('created_for', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='reviews_received', to='account.freelancer')),
                ('projects', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='projects_completed', to='FreelanceTask.project')),
            ],
            options={
                'db_table': 'Review',
            },
        ),
        migrations.CreateModel(
            name='Hire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('freelancer_accepted', models.BooleanField(default=False)),
                ('freelancer_rejected', models.BooleanField(default=False)),
                ('project_title', models.CharField(default='', max_length=255)),
                ('hiring_budget', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('message', models.TextField(default='')),
                ('hiring_budget_type', models.CharField(choices=[('Hourly', 'hourly'), ('Fixed', 'fixed')], default='', max_length=15)),
                ('hired_at', models.DateTimeField(auto_now_add=True)),
                ('hired_freelancer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='hired_freelancers', to='account.freelancer')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='hired_projects', to='FreelanceTask.project')),
            ],
            options={
                'db_table': 'Hire',
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
                ('project_pdf', models.FileField(blank=True, default='doc/default.pdf', upload_to='documents')),
                ('skills_used', models.CharField(default='', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.TextField(default='')),
                ('design_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='selfprojects', to='account.freelancer')),
            ],
            options={
                'db_table': 'FreelancerProject',
            },
        ),
        migrations.CreateModel(
            name='FreelancerNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField(default='')),
                ('is_read', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=50)),
                ('freelancer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='freelancer_notification', to='account.freelancer')),
            ],
            options={
                'db_table': 'FreelancerNotification',
            },
        ),
        migrations.CreateModel(
            name='FreelancerEmployment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Freelancer_Company_Name', models.CharField(default='', max_length=50)),
                ('Company_Designation', models.CharField(default='', max_length=100)),
                ('Company_Joining_date', models.DateField(blank=True, null=True)),
                ('Company_Leaving_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('add_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='employment', to='account.freelancer')),
            ],
            options={
                'db_table': 'FreelancerEmployment',
            },
        ),
        migrations.CreateModel(
            name='ClientNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField(default='')),
                ('is_read', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=50)),
                ('hirer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='hirer_notification', to='account.hirer')),
            ],
            options={
                'db_table': 'ClientNotification',
            },
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('bid_type', models.CharField(choices=[('Hourly', 'hourly'), ('Fixed', 'fixed')], default='', max_length=15)),
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
