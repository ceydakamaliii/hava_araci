# Generated by Django 5.0.8 on 2025-02-03 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_alter_team_team_type_alter_user_first_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="team",
            name="team_type",
            field=models.CharField(
                choices=[
                    ("WING", "Kanat Takımı"),
                    ("FUSELAGE", "Gövde Takımı"),
                    ("TAIL", "Kuyruk Takımı"),
                    ("AVIONICS", "Aviyonik Takımı"),
                    ("ASSEMBLY", "Montaj Takımı"),
                ],
                default="WING",
                max_length=20,
                unique=True,
                verbose_name="Takım Türü",
            ),
        ),
    ]
