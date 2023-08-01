# Generated by Django 4.2.3 on 2023-07-31 09:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
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
                ('category', models.CharField(choices=[('Web_development', 'web_development'), ('Mobile_development', 'mobile_development'), ('Web_designing', 'web_designing'), ('Software_development', 'software_development'), ('Ui_Ux_designing', 'ui_ux_designing'), ('Logo_Designing', 'logo_Designing'), ('Graphics_designing', 'graphics_designing'), ('Cloud_computing', 'cloud_computing'), ('AI_ML', 'AI_ML'), ('Data_Science', 'data_Science')], default='')),
                ('project_owner', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='projects', to='account.hirer')),
            ],
            options={
                'db_table': 'Project',
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