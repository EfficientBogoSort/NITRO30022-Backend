# Generated by Django 4.1 on 2022-09-23 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0002_remove_file_id_alter_file_document_alter_file_title'),
        ('collection', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='id',
        ),
        migrations.AddField(
            model_name='collection',
            name='files',
            field=models.ManyToManyField(blank=True, to='files.file'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='name',
            field=models.CharField(max_length=30, primary_key=True, serialize=False),
        ),
    ]
