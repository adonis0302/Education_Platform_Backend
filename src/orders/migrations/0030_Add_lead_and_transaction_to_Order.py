# Generated by Django 4.1.10 on 2023-08-25 04:48

from django.db import migrations
from django.db import models
import django.db.models.deletion


def set_relations(apps, schema_editor):
    AmoCRMOrderLead = apps.get_model("amocrm", "AmoCRMOrderLead")
    AmoCRMOrderTransaction = apps.get_model("amocrm", "AmoCRMOrderTransaction")
    for lead in AmoCRMOrderLead.objects.all():
        lead.order.amocrm_lead = lead
        lead.order.save()
    for transaction in AmoCRMOrderTransaction.objects.all():
        transaction.order.amocrm_transaction = transaction
        transaction.order.save()

class Migration(migrations.Migration):
    dependencies = [
        ("amocrm", "0005_Add_lead_and_transaction_to_Order"),
        ("orders", "0029_DropGiftFields"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="amocrm_lead",
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="amocrm.amocrmorderlead"),
        ),
        migrations.AddField(
            model_name="order",
            name="amocrm_transaction",
            field=models.OneToOneField(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="amocrm.amocrmordertransaction"
            ),
        ),
        migrations.RunPython(set_relations),
    ]
