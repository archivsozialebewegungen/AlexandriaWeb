from django.conf.urls import include, url  # @UnresolvedImport
from django.contrib import admin  # @UnresolvedImport
import alexdbview

urlpatterns = [
    # Examples:
    # url(r'^$', 'alexandriaweb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', admin.site.urls),
    url(r'^alexandria/', include(alexdbview.urls)),
]
