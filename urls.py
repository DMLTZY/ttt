from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name = 'demo'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^test/$', views.test, name='test'),
    url(r'^register/$', views.Registraion.as_view(), name='register'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^add-to-cart/$', views.add_to_cart, name='add_to_cart'),
    url(r'^cart/$', views.cart, name='cart'),
    url(r'^del-item/$', views.del_item, name='del_item'),
    url(r'^chg-item/$', views.chg_item, name='chg_item'),
    url(r'^apply/$', views.apply, name='apply'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^about/$', views.about, name='about'),
    url(r'^(?P<slug>[-a-z]*)/$', views.index, name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.Detail.as_view(), name='detail'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
