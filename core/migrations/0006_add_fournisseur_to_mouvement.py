# Generated by Django 4.2.7 on 2025-05-01 18:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_quantite_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='mouvementstock',
            name='fournisseur',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.fournisseur'),
        ),
    ]
