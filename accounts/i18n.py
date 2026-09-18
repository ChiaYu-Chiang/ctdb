"""
This file contains strings which need i18n but doesn't have a place in any files.
They maybe appear in DB only, so they can't be detected without being writed explicitly.
"""
from django.utils.translation import gettext_lazy as _

I18N_NEEDED = [
    # T00 (處)
    _('T00 member'),
    _('T00 supervisor'),
    _('T00 assistant'),

    # T11
    _('T11 member'),
    _('T11 supervisor'),
    _('T11 deputy'),
    _('T11 document controller'),

    # T12
    _('T12 member'),
    _('T12 supervisor'),
    _('T12 deputy'),
    _('T12 document controller'),

    # T13
    _('T13 member'),
    _('T13 supervisor'),
    _('T13 deputy'),
    _('T13 document controller'),

    # T15
    _('T15 member'),
    _('T15 supervisor'),
    _('T15 deputy'),
    _('T15 document controller'),

    # I00 (處)
    _('I00 member'),
    _('I00 supervisor'),
    _('I00 assistant'),

    # I01
    _('I01 member'),
    _('I01 supervisor'),
    _('I01 deputy'),
    _('I01 document controller'),

    # I02
    _('I02 member'),
    _('I02 supervisor'),
    _('I02 deputy'),
    _('I02 document controller'),

    # I03
    _('I03 member'),
    _('I03 supervisor'),
    _('I03 deputy'),
    _('I03 document controller'),

    # I04
    _('I04 member'),
    _('I04 supervisor'),
    _('I04 deputy'),
    _('I04 document controller'),
]