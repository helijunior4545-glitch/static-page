from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(
        name="ContactMessage",
        fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=100, verbose_name="Nome")),
            ("email", models.EmailField(max_length=254, verbose_name="E-mail")),
            ("message", models.TextField(max_length=3000, verbose_name="Mensagem")),
            ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Recebida em")),
        ],
        options={"ordering": ["-created_at", "-pk"], "verbose_name": "Mensagem de contato", "verbose_name_plural": "Mensagens de contato"},
    )]
