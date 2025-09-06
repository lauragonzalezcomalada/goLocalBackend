from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

# Register your models here.
from .models import Bono, CampoReserva, EntradasForPlan, EventTemplate, PaymentEventsRanges, PaymentForUse, Place,Activity, PrivatePlan, PrivatePlanInvitation, Reserva, ReservaForm,Tag, Ticket,UserProfile,Promo,ItemPlan


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user','birth_date', 'location', 'rate']
    filter_horizontal = ('tags','activities','promos','siguiendo')  # Esto permite seleccionar múltiples tags de manera más fácil

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)  # Esto permite seleccionar múltiples tags de manera más fácil
    list_display = ['name','creador','startDateandtime','gratis']


class PromoAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)
    list_display = ['name','creador','startDateandtime']

admin.site.register(Promo, PromoAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

#class PrivatePlanAdmin(admin.ModelAdmin):
#    filter_horizontal = ['invited_users']
admin.site.register(PrivatePlan)
admin.site.register(PrivatePlanInvitation)
class ItemPlanAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ('people_in_charge',)
admin.site.register(ItemPlan,ItemPlanAdmin)

@admin.register(EntradasForPlan)
class EntradasForPlanAdmin(admin.ModelAdmin):
    list_display = ('titulo',)
   
admin.site.register(Place)
admin.site.register(Tag)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('entrada_titulo', 'entrada_activity_name', 'user_username')

    @admin.display(description="Título de entrada")
    def entrada_titulo(self, obj):
        return obj.entrada.titulo if obj.entrada else "-"

    @admin.display(description="Actividad")
    def entrada_activity_name(self, obj):
        return obj.entrada.activity.name if obj.entrada and obj.entrada.activity else "-"

    @admin.display(description="Usuario")
    def user_username(self, obj):
        return obj.user_profile.user.username if obj.user_profile and obj.user_profile.user else "-"

admin.site.register(Reserva)
@admin.register(CampoReserva)
class CampoReservaAdmin(admin.ModelAdmin):
    list_display = ('label','nombre')

@admin.register(ReservaForm)
class ReservaFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity_name', 'promo_name')

    @admin.display(description="Actividad")
    def activity_name(self, obj):
        return obj.activity.name if obj.activity else "-"

    @admin.display(description="Promo")
    def promo_name(self, obj):
        return obj.promo.name if obj.promo else "-"


admin.site.register(EventTemplate)
admin.site.register(Bono)
admin.site.register(PaymentForUse)


@admin.register(PaymentEventsRanges)
class PaymentEventsRangesAdmin(admin.ModelAdmin):
    list_display = ('name','start_range','end_range')    

