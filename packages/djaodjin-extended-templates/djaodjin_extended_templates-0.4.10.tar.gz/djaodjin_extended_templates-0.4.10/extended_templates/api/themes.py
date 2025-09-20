# Copyright (c) 2023, Djaodjin Inc.
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
#pylint: disable=no-member
from __future__ import unicode_literals

import logging, zipfile

from rest_framework import parsers, serializers, status
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView
from rest_framework.response import Response

from .serializers import NoModelSerializer, EditToolsSerializer
from ..compat import gettext_lazy as _
from ..docs import extend_schema, OpenApiResponse
from ..mixins import ThemePackageMixin
from ..models import EditTools
from ..themes import (install_theme as install_theme_base,
    install_theme_fileobj, remove_theme)


LOGGER = logging.getLogger(__name__)


class ThemePackageUploadBodySerializer(NoModelSerializer):

    files = serializers.CharField(
        help_text=_("Content of the theme package as a zip file."))


class ThemePackageUploadSerializer(NoModelSerializer):

    location = serializers.CharField(read_only=True,
        help_text=_("URL where the theme package was uploaded."))


class ThemeEditToolsAPIView(RetrieveUpdateAPIView):
    """
    Retrives edit tools toggle

    **Tags: themes, broker, appmodel

    **Examples

    .. code-block:: http

        GET /api/themes/tools HTTP/1.1

    responds

    .. code-block:: json

        {
          "show_edit_tools": true
        }
    """

    serializer_class = EditToolsSerializer

    def get_object(self):
        edit_tools = EditTools.objects.filter(user=self.request.user).first()
        if not edit_tools:
            edit_tools = EditTools(show_edit_tools=False)
        return edit_tools


    def put(self, request, *args, **kwargs):
        """
        Toggles edit tools on/off

        **Tags: themes, broker, appmodel

        **Examples

        .. code-block:: http

            POST /api/themes/tools HTTP/1.1

        .. code-block:: json

            {
              "show_edit_tools": true
            }

        responds

        .. code-block:: json

            {
              "show_edit_tools": true
            }
        """
        #pylint:disable=unused-argument,useless-parent-delegation
        return super(ThemeEditToolsAPIView, self).put(
            request, *args, **kwargs)

    def perform_update(self, serializer):
        show_edit_tools = serializer.validated_data['show_edit_tools']
        if show_edit_tools:
            EditTools.objects.update_or_create(
                user=self.request.user, show_edit_tools=show_edit_tools)
        else:
            EditTools.objects.filter(user=self.request.user).delete()


class ThemePackageListAPIView(ThemePackageMixin, GenericAPIView):

    parser_classes = (parsers.FormParser, parsers.MultiPartParser,
        parsers.JSONParser)
    serializer_class = ThemePackageUploadBodySerializer

    def install_theme(self, package_uri):
        install_theme_base(self.theme, package_uri, force=True)

    def delete(self, request, *args, **kwargs):
        """
        Removes custom theme

        Removes the custom theme templates and assets.

        Pages will be using the default theme after a reset.

        **Tags: themes, broker, appmodel

        **Examples

        .. code-block:: http

            DELETE /api/themes HTTP/1.1
        """
        #pylint:disable=unused-argument
        remove_theme(self.theme)
        return Response({'detail': _("reset to default theme")},
            status=status.HTTP_200_OK)

    @extend_schema(responses={
        200: OpenApiResponse(ThemePackageUploadSerializer)})
    def post(self, request, *args, **kwargs):
        """
        Uploads a theme package

        Uploads a theme package with templates that will override the default
        ones. See `references and tutorials on creating themes
        <https://www.djaodjin.com/docs/guides/themes/>`_ for details
        on the theme package structure and customizing the default templates.

        **Tags: themes, broker, appmodel

        **Examples

        .. code-block:: shell

            curl -i -u *api_key*:  -X POST -F file=@*package*.zip \
https://*mydomain*/api/themes

        .. code-block:: http

            POST /api/themes HTTP/1.1

            Content-Disposition: form-data; name="file"; filename="theme.zip"
            Content-Type: application/x-zip

        responds

        .. code-block:: json

            {
              "location": "https://themes.*mydomain*/"
            }
        """

        #pylint:disable=unused-argument
        package_uri = request.data.get('location', None)
        if package_uri and 'aws.com/' in package_uri:
            self.install_theme(package_uri)
        elif 'file' in request.FILES:
            package_file = request.FILES['file']
            LOGGER.info("install %s to %s", package_file.name, self.theme)
            try:
                with zipfile.ZipFile(package_file, 'r') as zip_file:
                    install_theme_fileobj(self.theme, zip_file, force=True)
            finally:
                if hasattr(package_file, 'close'):
                    package_file.close()
        else:
            return Response({'details': "no package_uri or file specified."},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(ThemePackageUploadSerializer().to_representation({
            'location': package_uri}))
