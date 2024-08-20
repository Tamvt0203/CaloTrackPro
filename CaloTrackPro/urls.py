from django.urls import path
from . import views
from .views import LoginView, RegisterView, UserUpdateView, RootView, FoodUserCreateView, FoodUserUpdateView, FoodUserDeleteView, WeightUpdateView,UserDetailView,FoodListView, FoodUserDetailView
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('user/<int:userid>/update/', UserUpdateView.as_view(), name='user-update'),
    path('', RootView.as_view(), name='root'), 
    path('update-food-user/', FoodUserUpdateView.as_view(), name='update-food-user'),
    path('delete-food-user/', FoodUserDeleteView.as_view(), name='delete-food-user'),
    path('update-weight/', WeightUpdateView.as_view(), name='update-weight'),
    path('user-detail/', UserDetailView.as_view(), name='user-detail'),
    path('foods/', FoodListView.as_view(), name='food-list'),
    path('food-users/', FoodUserDetailView.as_view(), name='food-user-list'),
    path('add-food-user/', FoodUserCreateView.as_view(), name='add-food-user')
]