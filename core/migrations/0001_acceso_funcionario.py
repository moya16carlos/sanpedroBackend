from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='AccesoFuncionario',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('nombre', models.CharField(max_length=200, blank=True, null=True)),
                ('rol', models.CharField(max_length=50, default='FUNCIONARIO')),
                ('activo', models.BooleanField(default=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'accesos_funcionarios',
            },
        ),
    ]