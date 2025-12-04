from django.urls import include, re_path  # @UnresolvedImport
from django.contrib import admin  # @UnresolvedImport
import alexdbview

urlpatterns = [
    # Examples:
    # url(r'^$', 'alexandriaweb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    re_path(r'^admin/', admin.site.urls),
    re_path(r'^alexandria/', include(alexdbview.urls)),
]
