import logging
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import DatabaseError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods
from .forms import ContactForm
from .models import ContactMessage

@require_http_methods(["GET", "POST"])
def contact(request):
    form = ContactForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            record = form.save()
        except DatabaseError:
            logging.getLogger(__name__).exception("Unable to store contact message")
            form.add_error(None, "Não foi possível salvar. Tente novamente.")
            return render(request, "contact.html", {"form": form}, status=503)
        messages.success(request, f"Mensagem recebida com sucesso. Protocolo #{record.pk}.")
        return redirect("contact")
    return render(request, "contact.html", {"form": form})

@staff_member_required(login_url="login")
@require_GET
def inbox(request):
    return render(request, "inbox.html", {"records": ContactMessage.objects.all()[:100]})

@require_GET
def health(request):
    try:
        list(ContactMessage.objects.values_list("pk", flat=True)[:1])
        return JsonResponse({"status": "ok", "database": "ready"})
    except DatabaseError:
        return JsonResponse({"status": "unavailable"}, status=503)
