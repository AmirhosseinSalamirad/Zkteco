# Generated by Django 4.2.3 on 2023-07-29 21:39

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Devices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=50)),
                ('port', models.IntegerField()),
                ('serial_number', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=50)),
                ('timeout', models.IntegerField()),
                ('comment', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='OdooInstances',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('endpoint', models.TextField()),
                ('timeout', models.IntegerField()),
                ('batch_size', models.IntegerField()),
                ('ignore_ssl', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DeviceUsers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('image', models.ImageField(upload_to='')),
                ('device_id', models.IntegerField()),
                ('devices', models.ManyToManyField(to='odoo.devices')),
                ('instances', models.ManyToManyField(to='odoo.odooinstances')),
            ],
        ),
        migrations.CreateModel(
            name='Attendances',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_time', models.DateTimeField()),
                ('punch', models.IntegerField()),
                ('status', models.IntegerField()),
                ('is_sent', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('device_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='odoo.devices')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='odoo.deviceusers')),
            ],
        ),
    ]