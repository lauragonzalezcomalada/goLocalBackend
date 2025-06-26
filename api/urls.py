from django.urls import path
from .views import (hello_world, place_detail,get_all_places,activities,private_plans, tags, user_profile,sign_in,
                    google_sign_in,updateActivityAssistance,update_user,promos,create_event,user_prorfile_from_uuid,search_users,update_item_details)
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('hello/', hello_world),
    path('places/', get_all_places, name='place-list'), 
    path('place/', place_detail, name='place_detail'),
    path('activities/',activities, name='activities'),
    path('tags/',tags, name='tags'),
    path('user/profile/', user_profile, name='user-profile'),
    path('createevent/', create_event, name='create_event'),
    path('signIn/',sign_in, name="sign_in"),
    path('auth/google/', google_sign_in, name="auth_google"),
    path('actualizar_asistencia/',updateActivityAssistance, name="updateActivityAssistance"),
    path('actualizar_usuario/',update_user, name="update_user"),
    path('promos/',promos, name="promos"),
    path('userProfile/', user_prorfile_from_uuid, name="user_prorfile_from_uuid"),
    path('search_users/', search_users, name="search_users"),
    path('private_plans/', private_plans, name="private_plans"),
    path('update_item/', update_item_details,name = "update_item_details")

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

