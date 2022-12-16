from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()

router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:favorite_id>/favorite/', views.FavoriteView.as_view()),
    path('users/subscriptions/', views.SubscriptionViewSet.as_view()),
    path('users/<int:pk>/subscribe/', views.SubscribeView.as_view()),

]
