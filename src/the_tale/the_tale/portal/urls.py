
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^developers-info/', django_urls.include(('the_tale.portal.developers_info.urls', 'developers-info')))]

urlpatterns += views.resource.get_urls()
