# Copyright (c) 2022, Djaodjin Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Convenience module for access of extended_templates app settings, which enforces
default settings when the main settings module does not contain
the appropriate settings.
"""

import os, sys

from django.conf import settings
from django.utils._os import safe_join

def theme_dir(account): #pylint:disable=unused-argument
    theme_base_dir = os.path.join(settings.RUN_DIR
        if hasattr(settings, 'RUN_DIR') else settings.BASE_DIR, 'themes')
    if account:
        return os.path.join(theme_base_dir, account)
    return theme_base_dir


_SETTINGS = {
    'ACCOUNT_MODEL': getattr(settings, 'AUTH_USER_MODEL', None),
    'ACCOUNT_URL_KWARG': None,
    'ACTIVE_THEME_CALLABLE': None,
    'APP_NAME': getattr(settings, 'APP_NAME',
        os.path.basename(settings.BASE_DIR)),
    'ASSETS_MAP': {},
    'ASSETS_CACHE_DIR': (
        settings.STATIC_ROOT if settings.STATIC_ROOT
        else settings.STATICFILES_DIRS[0]),
    'ASSETS_SOURCES_DIR': safe_join(
        settings.BASE_DIR, os.path.basename(settings.BASE_DIR),
        'static', 'scss'),
    'ASSETS_DIRS_CALLABLE': None,
    'AUTH_USER_MODEL': getattr(settings, 'AUTH_USER_MODEL', None),
    'BUILD_ABSOLUTE_URI_CALLABLE': None,
    'AWS_STORAGE_BUCKET_NAME':
        getattr(settings, 'AWS_STORAGE_BUCKET_NAME',
            getattr(settings, 'APP_NAME',
                None)),
    'BUCKET_NAME_FROM_FIELDS': ['bucket_name'],
    'DEFAULT_ACCOUNT_CALLABLE': '',
    'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL'),
    'DEFAULT_STORAGE_CALLABLE': '',
    'EMAILER_BACKEND': getattr(settings, 'EMAILER_BACKEND',
        'extended_templates.backends.TemplateEmailBackend'),
    'EXTRA_FIELD': None,
    'EXTRA_MIXIN': object,
    'MEDIA_PREFIX': '',
    'MEDIA_URL': getattr(settings, 'MEDIA_URL'),
    'MEDIA_ROOT': getattr(settings, 'MEDIA_ROOT'),
    'PUBLIC_ROOT': (getattr(settings, 'STATIC_ROOT')
        if getattr(settings, 'STATIC_ROOT')
        else getattr(settings, 'STATICFILES_DIRS')[0]),
    'PUBLIC_WHITELIST': None,
    'PDF_FLATFORM_BIN': safe_join(
        os.path.dirname(sys.executable), 'podofo-flatform'),
    'SASSC_BIN': safe_join(
        os.path.dirname(sys.executable), 'sassc'),
    'SHOW_EDIT_TOOLS': None,
    'STATIC_URL': getattr(settings, 'STATIC_URL', '/static/'),
    'TEMPLATES_BLACKLIST': [],
    'TEMPLATES_WHITELIST': None,
    'THEME_DIR_CALLABLE': theme_dir,
}
_SETTINGS.update(getattr(settings, 'EXTENDED_TEMPLATES', {}))

ACCOUNT_MODEL = _SETTINGS.get('ACCOUNT_MODEL')
ACCOUNT_URL_KWARG = _SETTINGS.get('ACCOUNT_URL_KWARG')
ACTIVE_THEME_CALLABLE = _SETTINGS.get('ACTIVE_THEME_CALLABLE')
APP_NAME = _SETTINGS.get('APP_NAME')
AWS_STORAGE_BUCKET_NAME = _SETTINGS.get('AWS_STORAGE_BUCKET_NAME')
ASSETS_MAP = _SETTINGS.get('ASSETS_MAP')
ASSETS_CACHE_DIR = _SETTINGS.get('ASSETS_CACHE_DIR')
ASSETS_SOURCES_DIR = _SETTINGS.get('ASSETS_SOURCES_DIR')
ASSETS_DIRS_CALLABLE = _SETTINGS.get('ASSETS_DIRS_CALLABLE')
AUTH_USER_MODEL = _SETTINGS.get('AUTH_USER_MODEL')
BUCKET_NAME_FROM_FIELDS = _SETTINGS.get('BUCKET_NAME_FROM_FIELDS')
BUILD_ABSOLUTE_URI_CALLABLE = _SETTINGS.get('BUILD_ABSOLUTE_URI_CALLABLE')
DEFAULT_ACCOUNT_CALLABLE = _SETTINGS.get('DEFAULT_ACCOUNT_CALLABLE')
DEFAULT_FROM_EMAIL = _SETTINGS.get('DEFAULT_FROM_EMAIL')
DEFAULT_STORAGE_CALLABLE = _SETTINGS.get('DEFAULT_STORAGE_CALLABLE')
EMAILER_BACKEND = _SETTINGS.get('EMAILER_BACKEND')
PDF_FLATFORM_BIN = _SETTINGS.get('PDF_FLATFORM_BIN')
SASSC_BIN = _SETTINGS.get('SASSC_BIN')
STATIC_URL = _SETTINGS.get('STATIC_URL')
EXTRA_FIELD = _SETTINGS.get('EXTRA_FIELD')
EXTRA_MIXIN = _SETTINGS.get('EXTRA_MIXIN')
MEDIA_PREFIX = _SETTINGS.get('MEDIA_PREFIX')
MEDIA_URL = _SETTINGS.get('MEDIA_URL')
MEDIA_ROOT = _SETTINGS.get('MEDIA_ROOT')
PUBLIC_ROOT = _SETTINGS.get('PUBLIC_ROOT')
PUBLIC_WHITELIST = _SETTINGS.get('PUBLIC_WHITELIST')
SHOW_EDIT_TOOLS = _SETTINGS.get('SHOW_EDIT_TOOLS')
TEMPLATES_BLACKLIST = _SETTINGS.get('TEMPLATES_BLACKLIST')
TEMPLATES_WHITELIST = _SETTINGS.get('TEMPLATES_WHITELIST')
THEME_DIR_CALLABLE = _SETTINGS.get('THEME_DIR_CALLABLE')

LANGUAGE_CODE = getattr(settings, 'LANGUAGE_CODE')

SLUG_RE = r'[a-zA-Z0-9_\-\+\.]+'
PATH_RE = r'([a-zA-Z0-9\-]+/)*[a-zA-Z0-9\-]*'
NON_EMPTY_PATH_RE = r'([a-zA-Z0-9\-]+/)*[a-zA-Z0-9\-]+'

BOOTSTRAP_EDITABLE_VARIABLES = [
    ('Colors', [
        {'property': '@gray-base', 'default': '#000', 'editor': 'color'},
        {'property': '@gray-darker', 'default': 'lighten(@gray-base, 13.5%)',
         'editor': 'color'},
        {'property': '@gray-dark', 'default': 'lighten(@gray-base, 20%)',
         'editor': 'color'},
        {'property': '@gray', 'default': 'lighten(@gray-base, 33.5%)',
         'editor': 'color'},
        {'property': '@gray-light', 'default': 'lighten(@gray-base, 46.7%)',
         'editor': 'color'},
        {'property': '@gray-lighter', 'default': 'lighten(@gray-base, 93.5%)',
         'editor': 'color'},
        {'property': '@brand-primary', 'default': 'darken(#428bca, 6.5%)',
         'editor': 'color'},
        {'property': '@brand-success', 'default': '#5cb85c',
         'editor': 'color'},
        {'property': '@brand-info', 'default': '#5bc0de',
         'editor': 'color'},
        {'property': '@brand-warning', 'default': '#f0ad4e',
         'editor': 'color'},
        {'property': '@brand-danger', 'default': '#d9534f',
         'editor': 'color'},
    ]),
    ('Buttons', [
        {'property': '@btn-font-weight', 'default': 'normal'},
        {'property': '@btn-default-color', 'default': '#333',
         'editor': 'color'},
        {'property': '@btn-default-bg', 'default': '#fff',
         'editor': 'color'},
        {'property': '@btn-default-border', 'default': '#ccc',
         'editor': 'color'},
        {'property': '@btn-primary-color', 'default': '#fff',
         'editor': 'color'},
        {'property': '@btn-primary-bg', 'default': '@brand-primary',
         'editor': 'color'},
        {'property': '@btn-primary-border',
         'default': 'darken(@btn-primary-bg, 5%)',
         'editor': 'color'},
        {'property': '@btn-success-color', 'default': '#fff',
         'editor': 'color'},
        {'property': '@btn-success-bg', 'default': '@brand-success',
         'editor': 'color'},
        {'property': '@btn-success-border',
         'default': 'darken(@btn-success-bg, 5%)',
         'editor': 'color'},
        {'property': '@btn-info-color', 'default': '#fff',
         'editor': 'color'},
        {'property': '@btn-info-bg', 'default': '@brand-info',
         'editor': 'color'},
        {'property': '@btn-info-border', 'default': 'darken(@btn-info-bg, 5%)',
         'editor': 'color'},
        {'property': '@btn-warning-color', 'default': '#fff',
         'editor': 'color'},
        {'property': '@btn-warning-bg', 'default': '@brand-warning',
         'editor': 'color'},
        {'property': '@btn-warning-border',
         'default': 'darken(@btn-warning-bg, 5%)',
         'editor': 'color'},
        {'property': '@btn-danger-color', 'default': '#fff',
         'editor': 'color'},
        {'property': '@btn-danger-bg', 'default': '@brand-danger',
         'editor': 'color'},
        {'property': '@btn-danger-border',
         'default': 'darken(@btn-danger-bg, 5%)',
         'editor': 'color'},
        {'property': '@btn-link-disabled-color', 'default': '@gray-light',
         'editor': 'color'},

    ]),
    ('Typography', [
        {'property': '@font-family-sans-serif',
         'default': '"Helvetica Neue", Helvetica, Arial, sans-serif'},
        {'property': '@font-family-serif',
         'default': 'Georgia, "Times New Roman", Times, serif'},
        {'property': '@font-family-monospace',
         'default': 'Menlo, Monaco, Consolas, "Courier New", monospace'},
        {'property': '@font-family-base', 'default': '@font-family-sans-serif'},
        {'property': '@font-size-base', 'default': '14px'},
        {'property': '@font-size-large',
         'default': 'ceil((@font-size-base * 1.25))'},
        {'property': '@font-size-small',
         'default': 'ceil((@font-size-base * 0.85))'},
        {'property': '@font-size-h1',
         'default': 'floor((@font-size-base * 2.6))'},
        {'property': '@font-size-h2',
         'default': 'floor((@font-size-base * 2.15))'},
        {'property': '@font-size-h3',
         'default': 'ceil((@font-size-base * 1.7))'},
        {'property': '@font-size-h4',
         'default': 'ceil((@font-size-base * 1.25))'},
        {'property': '@font-size-h5',
         'default': '@font-size-base'},
        {'property': '@font-size-h6',
         'default': 'ceil((@font-size-base * 0.85))'},
        {'property': '@line-height-base', 'default': '1.428571429'},
        {'property': '@line-height-computed',
         'default': 'floor((@font-size-base * @line-height-base))'},
        {'property': '@headings-font-family', 'default': 'inherit'},
        {'property': '@headings-font-weight', 'default': '500'},
        {'property': '@headings-line-height', 'default': '1.1'},
        {'property': '@headings-color', 'default': 'inherit',
         'editor': 'color'},
    ]),
]
