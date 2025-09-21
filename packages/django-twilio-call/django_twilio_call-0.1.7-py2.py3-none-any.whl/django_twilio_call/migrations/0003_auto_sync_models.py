"""Auto-generated migration to sync models with database."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Add any missing fields to sync with model definitions."""

    dependencies = [
        ('django_twilio_call', '0002_optimize_database_indexes'),
    ]

    operations = [
        # The TwilioSIDMixin adds a twilio_sid field to Call model
        # But we already have this in 0001_initial, so check for other missing fields

        # Check if Call model is missing any fields
        migrations.AlterField(
            model_name='call',
            name='twilio_sid',
            field=models.CharField(db_index=True, help_text='Twilio resource identifier', max_length=50, unique=True, verbose_name='Twilio SID'),
        ),

        # PhoneNumber also has TwilioSIDMixin
        migrations.AlterField(
            model_name='phonenumber',
            name='twilio_sid',
            field=models.CharField(blank=True, db_index=True, help_text='Twilio resource identifier', max_length=50, unique=True, verbose_name='Twilio SID'),
        ),

        # Update price fields with help_text from PricingMixin
        migrations.AlterField(
            model_name='call',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=4, help_text='Cost in the specified currency', max_digits=10, null=True, verbose_name='price'),
        ),
        migrations.AlterField(
            model_name='call',
            name='price_unit',
            field=models.CharField(blank=True, default='USD', help_text='Currency code for the price', max_length=10, verbose_name='price unit'),
        ),

        migrations.AlterField(
            model_name='phonenumber',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=4, help_text='Cost in the specified currency', max_digits=10, null=True, verbose_name='price'),
        ),
        migrations.AlterField(
            model_name='phonenumber',
            name='price_unit',
            field=models.CharField(blank=True, default='USD', help_text='Currency code for the price', max_length=10, verbose_name='price unit'),
        ),

        # Ensure all timestamp fields have db_index where needed
        migrations.AlterField(
            model_name='agent',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='call',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='queue',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='phonenumber',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='callrecording',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='calllog',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='agentactivity',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='taskexecution',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='webhooklog',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at'),
        ),

        # Update help_text for metadata fields
        migrations.AlterField(
            model_name='agent',
            name='metadata',
            field=models.JSONField(blank=True, default=dict, help_text='Additional JSON data', verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='call',
            name='metadata',
            field=models.JSONField(blank=True, default=dict, help_text='Additional JSON data', verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='queue',
            name='metadata',
            field=models.JSONField(blank=True, default=dict, help_text='Additional JSON data', verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='phonenumber',
            name='metadata',
            field=models.JSONField(blank=True, default=dict, help_text='Additional JSON data', verbose_name='metadata'),
        ),
    ]