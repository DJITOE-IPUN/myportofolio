from django.db import migrations, models


def add_missing_columns(apps, schema_editor):
    connection = schema_editor.connection
    table_name = 'main_experience'
    existing_columns = {
        column.name
        for column in connection.introspection.get_table_description(
            connection.cursor(), table_name
        )
    }
    columns = {
        'organization': "varchar(255) NOT NULL DEFAULT ''",
        'location': "varchar(255) NOT NULL DEFAULT 'Depok, West Java'",
        'date_range': "varchar(100) NOT NULL DEFAULT ''",
    }
    for name, definition in columns.items():
        if name not in existing_columns:
            schema_editor.execute(
                f'ALTER TABLE {table_name} ADD COLUMN {name} {definition}'
            )


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_missing_columns, migrations.RunPython.noop),
        migrations.AddField(
            model_name='experience',
            name='is_ongoing',
            field=models.BooleanField(default=False),
        ),
    ]
