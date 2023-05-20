"""OfertApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from django.conf import settings
from django.conf.urls.static import static
import auth.urls as authUrls
import publications.urls as publicationsUrls
import comments.urls as commentsUrls
import util.urls as utilUrls
import transactions.urls as transactionsUrls
import core.urls as coreUrls
import payments.urls as paymentsUrls
import notifications.urls as notificationsUrls
import admins.urls as adminsUrls
import reports.urls as reportsUrls

apiUrl = 'api/v1/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(apiUrl, include( authUrls) ),
    path(apiUrl, include( publicationsUrls)),
    path(apiUrl, include( commentsUrls)),
    path(apiUrl, include( utilUrls)),
    path(apiUrl, include( transactionsUrls)),
    path(apiUrl, include( coreUrls)),
    path(apiUrl, include( paymentsUrls)),
    path(apiUrl, include( notificationsUrls)),
    path(apiUrl, include( adminsUrls)),
    path(apiUrl, include( reportsUrls)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )