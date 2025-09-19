from django.urls import path

from api.serializers import CampoReservaSerializer
from .views import (CustomTokenObtainPairView, ableToTurnVisible, accept_invitation, add_item, billingStatus, bonos, camposReserva, create_ticket, createCompraSimple, createReserva, createSplitPayment, entradasForUserAdmin, eventosActivos, export_to_excel, failureMP, generateOauthMpLink, get_tickets, hello_world, invitation_redirect, pendingMP, registerShare, registerView, obtainAccessTokenVendedor, paymentEventsRanges, place_detail,get_all_places,activities,private_plans, successMP, tags, updateActiveStatus, updateEntrada, updatePassword, updateReserva, updateReservaStatus, updateTicketsLink, user_profile,sign_in,
                    google_sign_in,updateActivityAssistance,update_user,promos,create_event,user_prorfile_from_uuid,search_users,update_item_details, userCreatedEventsForTheWeek, validate_ticket,soldTicketsForEvent, templates, webhook_mp)
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/creador/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair_creador'),
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
    path('update_item/', update_item_details,name = "update_item_details"),
    path('add_item/', add_item, name="add_item"),
    path('accept_invitation/', accept_invitation, name='accept_invitation'),
    path('i/<str:invitation_code>/', invitation_redirect, name='invitation-redirect'),
    path('validate_ticket/', validate_ticket, name='validate_ticket'),
    path('create_tickets/', create_ticket, name='create_ticket'),
    path('get_tickets/', get_tickets, name="get_tickets"),
    path('create_reserva/', createReserva, name="create-reserva"),

    ##Aquí aniran les calls només pel goLocalWeb
    path('events_for_the_week/', userCreatedEventsForTheWeek, name="userCreatedEventsForTheWeek"),
    path('entradas_user_admin/', entradasForUserAdmin, name="entradasForUserAdmin"),
    path('sold_tickets_for_event/',soldTicketsForEvent, name = "soldTicketsForEvent"),
    path('update_entrada/', updateEntrada, name ="updateEntrada"),
    path('update_reserva/', updateReserva, name = "updateReserva"),
    path('campos_reserva/', camposReserva, name='camposReserva'),   
    path('templates/', templates, name='templates'),
    path('update_reserva_status/', updateReservaStatus, name="updateReservaStatus"),
    path('update_tickets_link/', updateTicketsLink, name="updateTicketsLink"),
    path('handle_visibility_change/', updateActiveStatus, name="updateActiveStatus"),
    path('update_pwd/', updatePassword, name="updatePassword"),
    path('able_turn_visible/', ableToTurnVisible, name="ableToTurnVisible"),
    path('billing_status/', billingStatus, name="billingStatus"),
    path('bonos/', bonos, name="bonos"),
    path('payment_events_ranges/', paymentEventsRanges, name="paymentEventsRanges"),
    path('export-pagos-excel/', export_to_excel, name="export_to_excel"),
    path('register_view/', registerView, name="registerView"),
    path('register_share/', registerShare, name="registerShare"),

    #mercadopago
    path('generate_oauth_mp_link/', generateOauthMpLink, name="generate_oauth_mp_link"),
    path('success_oauth_registration/', obtainAccessTokenVendedor, name="getAccessTokenVendedor"),
    path('create_split_payment/', createSplitPayment, name="createSplitPayment"),
    path('success/', successMP, name="success_mp"),
    path('failure/', failureMP, name="failure_mp"),
    path('pending/', pendingMP, name="pending_mp"),
    path('crear_compra_simple/', createCompraSimple, name="createCompraSimple"),
    path('webhook_mp/', webhook_mp, name="webhook_mp"),

    #goLocalQR
    path('eventos_activos/', eventosActivos, name="eventos_activos"),

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

