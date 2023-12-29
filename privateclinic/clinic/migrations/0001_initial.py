# Generated by Django 5.0 on 2023-12-28 07:37

import cloudinary.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Medicine",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Doctor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=80, null=True)),
                ("last_name", models.CharField(max_length=80, null=True)),
                ("birth_date", models.DateField(null=True)),
                (
                    "sex",
                    models.CharField(
                        choices=[("Male", "Male"), ("Female", "Female")],
                        max_length=10,
                        null=True,
                    ),
                ),
                ("cin", models.CharField(max_length=15, null=True)),
                ("phone_nb", models.CharField(max_length=30, null=True)),
                ("email", models.EmailField(max_length=254)),
                ("pwd", models.CharField(max_length=200)),
                ("salary", models.FloatField()),
                (
                    "specialty",
                    models.CharField(
                        choices=[
                            ("G", "General practice"),
                            ("C", "Clinical radiology"),
                            ("A", "Anaesthesia"),
                            ("O", "Ophthalmology"),
                        ],
                        max_length=200,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created", models.DateField(auto_now_add=True)),
                (
                    "user",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Nurse",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=80, null=True)),
                ("last_name", models.CharField(max_length=80, null=True)),
                ("birth_date", models.DateField(null=True)),
                (
                    "sex",
                    models.CharField(
                        choices=[("Male", "Male"), ("Female", "Female")],
                        max_length=10,
                        null=True,
                    ),
                ),
                ("cin", models.CharField(max_length=15, null=True)),
                ("phone_nb", models.CharField(max_length=30, null=True)),
                ("salary", models.FloatField()),
                ("is_active", models.BooleanField(default=True)),
                ("created", models.DateField(auto_now_add=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("scheduled_time", models.DateTimeField()),
                ("confirmed", models.BooleanField(default=False)),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "doctor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="clinic.doctor"
                    ),
                ),
                (
                    "nurse",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="clinic.nurse"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Patient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=80, null=True)),
                ("last_name", models.CharField(max_length=80, null=True)),
                ("birth_date", models.DateField(null=True)),
                (
                    "sex",
                    models.CharField(
                        choices=[("Male", "Male"), ("Female", "Female")],
                        max_length=10,
                        null=True,
                    ),
                ),
                ("cin", models.CharField(max_length=15, null=True)),
                ("phone_nb", models.CharField(max_length=30, null=True)),
                (
                    "avatar",
                    cloudinary.models.CloudinaryField(
                        max_length=255, null=True, verbose_name="avatar"
                    ),
                ),
                ("email", models.EmailField(max_length=254, null=True)),
                ("weight", models.IntegerField(null=True)),
                ("allergies", models.CharField(max_length=200, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Prescription",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("symptoms", models.TextField()),
                ("diagnosis", models.TextField()),
                (
                    "appointment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="clinic.appointment",
                    ),
                ),
                ("medicines", models.ManyToManyField(to="clinic.medicine")),
            ],
        ),
    ]