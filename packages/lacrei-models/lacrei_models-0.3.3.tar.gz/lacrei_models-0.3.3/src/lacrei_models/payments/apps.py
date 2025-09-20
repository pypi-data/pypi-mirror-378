from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class PaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'lacrei_models.payments'
    label = 'payments'
    verbose_name = _('Pagamentos')