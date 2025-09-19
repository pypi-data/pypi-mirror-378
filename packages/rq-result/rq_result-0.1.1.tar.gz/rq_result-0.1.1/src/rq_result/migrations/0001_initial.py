import uuid

from django.db import migrations, models

from ..models import Job


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('job_id',
                 models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=128)),
                ('meta', models.JSONField(blank=True, default=dict)),
                ('kwargs', models.JSONField(blank=True, default=dict)),
                ('queue', models.CharField(max_length=128)),
                ('status', models.CharField(
                    choices=[('created', 'Created'), ('queued', 'Queued'),
                             ('started', 'Started'), ('running', 'Running'),
                             ('finished', 'Finished'), ('successful', 'Successful'),
                             ('failed', 'Failed'), ('timeout', 'Timeout'),
                             ('cancelled', 'Cancelled'), ('stopped', 'Stopped'),
                             ('deferred', 'Deferred'), ('scheduled', 'Scheduled')],
                    default='created', max_length=10)),
                ('group_id', models.CharField(blank=True, max_length=128, null=True)),
                ('worker_name',
                 models.CharField(blank=True, max_length=128, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('inventory', models.CharField(blank=True, max_length=255, null=True)),
                ('timeout', models.SmallIntegerField(blank=True, default=3600)),
                ('ttl', models.SmallIntegerField(blank=True, null=True)),
                ('result_ttl', models.SmallIntegerField(blank=True, default=500)),
                ('failure_ttl', models.SmallIntegerField(blank=True, default=604800)),
                ('success_callback_name',
                 models.CharField(blank=True, max_length=128, null=True)),
                ('failure_callback_name',
                 models.CharField(blank=True, max_length=128, null=True)),
                ('stopped_callback_name',
                 models.CharField(blank=True, max_length=128, null=True)),
                ('rc', models.SmallIntegerField(blank=True, null=True)),
                ('result', models.TextField(blank=True, null=True)),
                ('exc_info', models.TextField(blank=True, null=True)),
                ('last_heartbeat', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('enqueued_at', models.DateTimeField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'verbose_name': 'Job',
                'verbose_name_plural': 'Jobs',
                'db_table': Job.Meta.db_table,
                'abstract': False,
                'swappable': 'JOB_MODEL',
            },
        ),
    ]
