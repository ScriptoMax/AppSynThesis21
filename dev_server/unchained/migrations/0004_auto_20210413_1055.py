# Generated by Django 3.2 on 2021-04-13 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('unchained', '0003_auto_20210413_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commoninfoprovisionreport',
            name='subcategory_code',
            field=models.ForeignKey(blank=True, default=201, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='commoninfoprovisionreport', to='unchained.subcategory'),
        ),
        migrations.AlterField(
            model_name='contactcancelreport',
            name='subcategory_code',
            field=models.ForeignKey(blank=True, default=201, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='contactcancelreport', to='unchained.subcategory'),
        ),
        migrations.AlterField(
            model_name='customerdiscontentreport',
            name='subcategory_code',
            field=models.ForeignKey(blank=True, default=201, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='customerdiscontentreport', to='unchained.subcategory'),
        ),
        migrations.AlterField(
            model_name='prospectdealreport',
            name='subcategory_code',
            field=models.ForeignKey(blank=True, default=201, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prospectdealreport', to='unchained.subcategory'),
        ),
        migrations.AlterField(
            model_name='technicalissuereport',
            name='subcategory_code',
            field=models.ForeignKey(blank=True, default=201, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='technicalissuereport', to='unchained.subcategory'),
        ),
        migrations.AlterField(
            model_name='useraccountcontrolreport',
            name='subcategory_code',
            field=models.ForeignKey(blank=True, default=201, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='useraccountcontrolreport', to='unchained.subcategory'),
        ),
        migrations.AlterField(
            model_name='useraccountinforeport',
            name='subcategory_code',
            field=models.ForeignKey(blank=True, default=201, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='useraccountinforeport', to='unchained.subcategory'),
        ),
    ]
