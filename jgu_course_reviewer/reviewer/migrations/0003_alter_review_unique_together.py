# Generated by Django 4.2.18 on 2025-02-12 11:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviewer', '0002_course_avg_rating'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='review',
            unique_together={('author', 'course_instructor_term')},
        ),
    ]
