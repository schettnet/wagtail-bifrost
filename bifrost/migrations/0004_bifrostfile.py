# Generated by Django 3.1.7 on 2021-03-31 21:59

import bifrost.files.models
from django.db import migrations, models
import private_storage.fields
import private_storage.storage.files
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bifrost', '0003_delete_stubmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='BifrostFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(default=bifrost.files.models.generate_key, max_length=40)),
                ('file', private_storage.fields.PrivateFileField(storage=private_storage.storage.files.PrivateFileSystemStorage(), upload_to='')),
                ('group', models.CharField(blank=True, max_length=32, null=True)),
                ('ubfn', models.CharField(default=uuid.uuid4, max_length=32, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
