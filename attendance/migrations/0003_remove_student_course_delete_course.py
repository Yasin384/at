# Generated by Django 5.1.1 on 2024-09-27 07:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_remove_course_faculty_course_faculties'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='course',
        ),
        migrations.DeleteModel(
            name='Course',
        ),
    ]
