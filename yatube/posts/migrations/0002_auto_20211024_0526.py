# Generated by Django 2.2.19 on 2021-10-24 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('slug', models.SlugField()),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='group',
            field=models.SlugField(blank=True, null=True),
        ),
    ]
