from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class BaseLacreisaudeConfig(AppConfig):
    name = 'lacrei_models.lacreisaude'
    label = 'lacreisaude'
    verbose_name = _('Lacrei Saúde')