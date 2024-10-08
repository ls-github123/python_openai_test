# Generated by Django 5.1.1 on 2024-09-22 12:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CatesModel',
            fields=[
                ('code', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True, verbose_name='会话编码')),
                ('title', models.CharField(blank=True, max_length=50, null=True, verbose_name='会话标题')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '会话分组',
                'verbose_name_plural': '会话分组',
                'db_table': 'cates_model',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='QuestionModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ask', models.CharField(blank=True, max_length=100, null=True, verbose_name='会话提问')),
                ('answer', models.TextField(blank=True, verbose_name='回复内容')),
                ('response_time', models.DateTimeField(auto_now_add=True, verbose_name='回复时间')),
                ('cid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='api.catesmodel', verbose_name='对应分组')),
            ],
            options={
                'verbose_name': '会话内容',
                'verbose_name_plural': '会话内容',
                'db_table': 'question_model',
                'managed': True,
            },
        ),
    ]
