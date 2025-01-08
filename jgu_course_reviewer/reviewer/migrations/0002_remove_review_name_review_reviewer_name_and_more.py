# Generated by Django 4.2.4 on 2024-11-22 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviewer', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='name',
        ),
        migrations.AddField(
            model_name='review',
            name='reviewer_name',
            field=models.CharField(default='Anonymous', max_length=255),
        ),
        migrations.AddField(
            model_name='term',
            name='term_season',
            field=models.CharField(choices=[('Spring', 'Spring'), ('Fall', 'Fall')], default='Spring', max_length=6),
        ),
        migrations.AddField(
            model_name='term',
            name='term_year',
            field=models.PositiveIntegerField(default=2024),
        ),
        migrations.AlterField(
            model_name='term',
            name='term_name',
            field=models.CharField(editable=False, max_length=20, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='term',
            unique_together={('term_season', 'term_year')},
        ),
    ]
