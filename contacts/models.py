from django.db import models

class ContactMessage(models.Model):
    name = models.CharField("Nome", max_length=100)
    email = models.EmailField("E-mail")
    message = models.TextField("Mensagem", max_length=3000)
    created_at = models.DateTimeField("Recebida em", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "Mensagem de contato"
        verbose_name_plural = "Mensagens de contato"

    def __str__(self):
        return f"{self.name} — #{self.pk}"
