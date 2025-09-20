from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppointmentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lacrei_models.appointments"
    label = "appointments"
    verbose_name = _("Agendamentos")