# Generated by Django 3.0.6 on 2020-05-13 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Submissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('poster', models.CharField(max_length=20)),
                ('queried_at', models.DateTimeField(auto_now_add=True)),
                ('submission_id', models.CharField(max_length=7)),
                ('subreddit', models.CharField(max_length=20)),
                ('num_comments', models.IntegerField()),
                ('sha256', models.CharField(max_length=64)),
            ],
            options={
                'ordering': ['id', 'queried_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='submissions',
            constraint=models.UniqueConstraint(fields=('sha256',), name='unique comment state'),
        ),
    ]
