# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url('admin/', admin.site.urls),
]
