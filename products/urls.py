from django.urls import path
from . import views

# url from /products/

app_name = 'products'
urlpatterns = [
    path('', views.FavouritesView.as_view(), name='index'),
    path('search/', views.ProductsView.as_view(), name='search'),
    path('compare/<int:pk>', views.CompareView.as_view(), name='compare'),
    path('<int:pk>', views.ProductDetailView.as_view(), name='detail'),
    path('save/<int:pk_health>/<int:pk_unhealth>', views.save, name='save'),
    path(
        'delete/<int:pk_health>/<int:pk_unhealth>',
        views.delete, name='delete')
]
