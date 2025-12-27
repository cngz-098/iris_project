from django.urls import path, include 
from . import views
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter 

# API için router tanımlıyoruz
router = DefaultRouter()
router.register(r'observations', views.IrisObservationViewSet) # Views içindeki ViewSet'i bağladım

urlpatterns = [
    path('', views.home_or_public, name='home'),
path('dashboard/', views.home_or_public, name='dashboard'),

    path('signin/', views.signin_view, name='signin'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    path('iris/', views.iris_list, name='iris_list'),
    path('iris/add/', views.iris_create, name='iris_create'),
    path('iris/update/<int:pk>/', views.iris_update, name='iris_update'),
    path('iris/delete/<int:pk>/', views.iris_delete, name='iris_delete'),
    
    path('export/', views.export_iris_csv, name='export_csv'),
    path('import/', views.import_iris_csv, name='import_csv'),
    path('predict/', views.predict_species, name='predict'),

    path('api/', include(router.urls)), # Tarayıcıda /api/observations/ olarak görünecek
]