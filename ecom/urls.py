from django.urls import path, include, re_path
import notifications.urls
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



router = DefaultRouter()
router.register('subcategory', views.SubCategoryViewSet, 'subcategory')
router.register('products', views.ProductViewSet)
router.register('cart', views.CartViewSet)
router.register('categories', views.CategoryViewSet)
router.register('nnotifications', views.NotificationViewSet)
router.register('wishlist', views.WishListApi)
router.register('shiping', views.ShippingApi)



urlpatterns = [
    path('', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('search/', views.SearchProducts.as_view()),
    re_path(r'^inbox/notifications/', include((notifications.urls, 'notifications'), namespace='notifications')),
    path('csv/', views.CSVUploadView.as_view()),
    path('csv_export/', views.CSVExportView.as_view()),

]