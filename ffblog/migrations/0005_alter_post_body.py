from django.db import migrations
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ffblog', '0004_category_post_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='body',
            field=django_ckeditor_5.fields.CKEditor5Field('Body', config_name='default'),
        ),
    ]