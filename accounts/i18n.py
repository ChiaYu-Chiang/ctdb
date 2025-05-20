"""
This file contains strings which need i18n but doesn't have a place in any files.
They maybe appear in DB only, so they can't be detected without being writed explicitly.
"""
from django.utils.translation import gettext_lazy as _

I18N_NEEDED = [
    _('T00 member'),
    _('T11 member'),
    _('T12 member'),
    _('T13 member'),
    _('T15 member'),
    _('I00 member'),
    _('I01 member'),
    _('I02 member'),
    _('I03 member'),
    _('I04 member'),
    _('T00 supervisor'),
    _('T11 supervisor'),
    _('T12 supervisor'),
    _('T13 supervisor'),
    _('T15 supervisor'),
    _('I00 supervisor'),
    _('I01 supervisor'),
    _('I02 supervisor'),
    _('I03 supervisor'),
    _('I04 supervisor'),
]
