from django.contrib import admin

# Register your models here.
from .models import Place,Activity, PrivatePlan, PrivatePlanInvitation,Tag,UserProfile,Promo,ItemPlan


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user','birth_date', 'originLocation', 'rate']
    filter_horizontal = ('tags','activities','promos','siguiendo')  # Esto permite seleccionar múltiples tags de manera más fácil

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)  # Esto permite seleccionar múltiples tags de manera más fácil
    list_display = ['name','creador','startDateandtime','gratis']


class PromoAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)

admin.site.register(Promo, PromoAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

#class PrivatePlanAdmin(admin.ModelAdmin):
#    filter_horizontal = ['invited_users']
admin.site.register(PrivatePlan)
admin.site.register(PrivatePlanInvitation)
class ItemPlanAdmin(admin.ModelAdmin):
    filter_horizontal = ('people_in_charge',)
admin.site.register(ItemPlan,ItemPlanAdmin)


admin.site.register(Place)
admin.site.register(Tag)



