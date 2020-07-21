# Generated by Django 2.0.6 on 2020-07-21 00:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0003_auto_20200717_0919'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_show', models.BooleanField(default=False, verbose_name='是否显示')),
                ('orders', models.IntegerField(default=1, verbose_name='图片排序')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('trade_no', models.CharField(blank=True, help_text='将来依靠流水号到支付平台查账单', max_length=128, null=True, verbose_name='支付平台的流水号')),
                ('buy_type', models.SmallIntegerField(choices=[(1, '用户购买'), (2, '免费活动'), (3, '活动赠品'), (4, '系统赠送')], default=1, verbose_name='购买方式')),
                ('pay_time', models.DateTimeField(blank=True, null=True, verbose_name='购买时间')),
                ('out_time', models.DateTimeField(blank=True, null=True, verbose_name='过期时间')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='course_users', to='course.Course', verbose_name='课程')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_courses', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '课程购买记录',
                'verbose_name_plural': '课程购买记录',
                'db_table': 'bz_user_course',
            },
        ),
    ]
