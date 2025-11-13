from datetime import date, datetime, time
from zoneinfo import ZoneInfo
from rest_framework import serializers
from .models import Bono, CampoReserva, EntradasForPlan, EventTemplate, PaymentEventsRanges, Place, Activity, PrivatePlan, PrivatePlanInvitation, Promo, Reserva, ReservaForm,Tag, Ticket,UserProfile, ItemPlan
from django.utils.dateparse import parse_datetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CreatorTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        if not hasattr(user, 'userprofile') or not user.userprofile.creador:
            raise serializers.ValidationError("No tienes permisos para acceder como creador")

        return data
    
class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    Un ModelSerializer que permite especificar dinámicamente los campos a incluir.
    """
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)  # Extraemos los campos personalizados
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class PlaceSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Place
        fields = '__all__'




class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id','name','icon']

class UserProfileBasicSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['uuid', 'username', 'image']

class CampoReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampoReserva
        fields = ['nombre', 'label', 'tipo']

class ReservasFormsSerializer(serializers.ModelSerializer):
    campos = CampoReservaSerializer(many=True, read_only=True)
    class Meta:
        model = ReservaForm
        fields = ['uuid', 'nombre', 'max_disponibilidad','campos','confirmados']
class EntradasForPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntradasForPlan
        fields = ['uuid', 'precio', 'titulo', 'desc', 'disponibles','maxima_disponibilidad']
class ActivitySerializer(DynamicFieldsModelSerializer):
    place_name = serializers.CharField(source='place.name', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    asistentes = UserProfileBasicSerializer(many=True, read_only=True, source='activities')  # Este es el campo nuevo

    tag_detail = TagSerializer(required=False, many=True,read_only=True, source='tags') #para el GET, que se muestra todo el Tag
    creador_image = serializers.SerializerMethodField()
    created_by_user = serializers.SerializerMethodField()
    creador = UserProfileBasicSerializer(many=False, read_only=True) 

    entradas_for_plan = EntradasForPlanSerializer(many=True, read_only=True)
    reservas_forms = ReservasFormsSerializer(many=True, read_only = True)
    user_isgoing = serializers.SerializerMethodField()

    disponibilidad_creacion = serializers.SerializerMethodField()
    recommendedAmount = serializers.IntegerField( required=False, allow_null=True)

    class Meta:
        model = Activity
        fields = '__all__'
    
    def get_creador_image(self, obj):
        user = obj.creador
        print('user')
        if hasattr(user, 'profile') and user.user.profile.image:
            return user.user.profile.image.url
        return None

    def get_created_by_user(self, obj):
        # Necesita acceso al usuario del contexto
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            
            return obj.creador.user == request.user
        return False
    
    def get_user_isgoing(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                user_profile = request.user.profile
                return obj in user_profile.activities.all()
            except UserProfile.DoesNotExist:
                return False
        return False
    
    def get_disponibilidad_creacion(self, obj):
        return True
    
from django.db.models import Sum
class ActivitySerializerForGoLocalQR(serializers.ModelSerializer):
    disponibles = serializers.SerializerMethodField()
    vendidas = serializers.SerializerMethodField()
    asistidos = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = ['uuid', 'name', 'startDateandtime', 'disponibles', 'vendidas', 'asistidos','image']

    def get_disponibles(self, obj):
        # Suma de max_disponibilidad de todas las entradas asociadas
        return obj.entradas_for_plan.aggregate(total=Sum('maxima_disponibilidad'))['total'] or 0

    def get_vendidas(self, obj):
        # Contar tickets asociados a todas las entradas de la actividad
        return Ticket.objects.filter(entrada__activity=obj).count()

    def get_asistidos(self, obj):
        # Contar tickets con status=1 asociados a todas las entradas de la actividad
        return Ticket.objects.filter(entrada__activity=obj, status=1).count()
    

class PromoSerializer(DynamicFieldsModelSerializer):

    place_name = serializers.CharField(source='place.name', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    tag_detail = TagSerializer(required=False, many=True,read_only=True, source='tags') #para el GET, que se muestra todo el Tag
    reservas_forms = ReservasFormsSerializer(many=True, read_only = True)
    asistentes = UserProfileBasicSerializer(many=True, read_only=True, source='promos')  
    user_isgoing = serializers.SerializerMethodField()
    creador_image = serializers.SerializerMethodField()
    created_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Promo
        fields = '__all__'
    
    def get_creador_image(self, obj):
        user = obj.creador
        if hasattr(user, 'profile') and user.profile.image:
            return user.profile.image.url
        return None

    def get_created_by_user(self, obj):
        # Necesita acceso al usuario del contexto
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            return obj.creador.user == request.user
        return False
    
    def get_user_isgoing(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                user_profile = request.user.profile
                return obj in user_profile.promos.all()
            except UserProfile.DoesNotExist:
                return False
        return False


from django.utils import timezone
class PaymentEventsRangesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentEventsRanges
        fields = ['uuid', 'name', 'start_range', 'end_range', 'price']

class UserProfileSerializerForQR(DynamicFieldsModelSerializer):
    today_activities = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)  # Nombre de usuario
    email = serializers.CharField(source='user.email', read_only=True) #email

    class Meta:
        model = UserProfile
        fields = [
            'uuid',
            'username',
            'bio',
            'location',
            'email',
            'image',
            'today_activities',
        ]

    def get_today_activities(self, obj):

        argentina_tz = ZoneInfo("America/Argentina/Buenos_Aires")
        today_ar = timezone.now().astimezone(argentina_tz).date()

        # Inicio y fin del día en horario argentino
        start_of_day_ar = datetime.combine(today_ar, time.min, tzinfo=argentina_tz)
        end_of_day_ar = datetime.combine(today_ar, time.max, tzinfo=argentina_tz)

        # Convertir a UTC para filtrar en DB
        start_of_day_utc = start_of_day_ar.astimezone(ZoneInfo("UTC"))
        end_of_day_utc = end_of_day_ar.astimezone(ZoneInfo("UTC"))

     
        activities = Activity.objects.filter(
            creador=obj.user,
            startDateandtime__range=(start_of_day_utc, end_of_day_utc),
            control_entradas=True,
            entradas_for_plan__isnull=False
        ).distinct()

    

        return ActivitySerializer(activities, many=True).data

class UserProfileSerializer(DynamicFieldsModelSerializer):
    tags = TagSerializer(many=True)
    username = serializers.CharField(source='user.username', read_only=True)  # Nombre de usuario
    email = serializers.CharField(source='user.email', read_only=True) #email
    payment_events_range = PaymentEventsRangesSerializer(read_only=True)   # activity_detail = ActivitySerializer(required=False, many=True,read_only=True, source='activities')
    can_create_free_plan = serializers.SerializerMethodField()
    can_create_payment_plan = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields =['uuid','user', 'username', 'email', 'bio', 'birth_date', 'creation_date', 'location', 'locationId', 'image', 'tags', 'activities', 'promos','siguiendo', 'telefono', 'can_create_free_plan', 'can_create_payment_plan','payment_events_range', 'creador', 'pago_suscripcion_mes_proximo',  'pago_suscripcion_mes_actual']

    
    def get_can_create_free_plan(self,obj):
        return obj.available_planes_gratis > 0
    
    def get_can_create_payment_plan(self,obj):
        
        start_month = date.today().replace(day=1)
        end_month = date.today().replace(day=28)
        active_activities_this_month =  Activity.objects.filter(
            creador=obj,
            gratis=False,
            active=True,
            startDateandtime__range=(start_month, end_month)
        ).count()

        if not obj.payment_events_range:
            return False
        return active_activities_this_month < obj.payment_events_range.end_range
        

    def to_representation(self, instance):
        # Aseguramos pasar el contexto con request
        rep = super().to_representation(instance)
        request = self.context.get('request')  
        # Obtenemos instancias relacionadas
        activities = instance.activities.all()
        promos = instance.promos.all()
        privateplans = instance.planes_invitados.all()

        eventos = []
        eventos_creados = []


        for activity in activities:
            has_ticket = Ticket.objects.filter(
                user_profile=instance,
                entrada__activity=activity
            ).exists()

            eventos.append({
                'type': 'activity',
                'uuid': activity.uuid,
                'name': activity.name,
                'image': activity.image.url if activity.image else None,
                'startDateandtime': activity.startDateandtime,
                'tiene_ticket': has_ticket,
                'created_by_user': activity.creador.user == request.user if request else False

            })
            
        for promo in promos:
            
            eventos.append({
                'type': 'promo',
                'uuid': promo.uuid,
                'name': promo.name,
                'image': promo.image.url if promo.image else None,
                'startDateandtime': promo.startDateandtime,
                'tiene_ticket': False,
                'created_by_user': promo.creador == request.user if request else False

            })

        for plan in privateplans:
            eventos.append({
                'type': 'privateplan',
                'uuid': plan.uuid,
                'name': plan.name,
                'image': plan.image.url if plan.image else None,
                'startDateandtime': plan.startDateandtime,
                'tiene_ticket': False,
                'asistentes': [inv.invited_user.uuid for inv in plan.privateplaninvitation_set.filter(status=1)],
                'created_by_user': plan.creador == request.user if request else False

            })

        activities_creadas = Activity.objects.filter(creador=instance)
        promos_creadas = Promo.objects.filter(creador=instance)
        planes_creados = PrivatePlan.objects.filter(creador=instance)

        for activity in activities_creadas:
            eventos_creados.append({
                'type': 'activity',
                'uuid': activity.uuid,
                'name': activity.name,
                'image': activity.image.url if activity.image else None,
                'startDateandtime': activity.startDateandtime,
                'created_by_user': True,
                'active': activity.active
            })

        for promo in promos_creadas:
            eventos_creados.append({
                'type': 'promo',
                'uuid': promo.uuid,
                'name': promo.name,
                'image': promo.image.url if promo.image else None,
                'startDateandtime': promo.startDateandtime,
                'created_by_user': True,
                'active':promo.active
            })

        for plan in planes_creados:
            eventos_creados.append({
                'type': 'privateplan',
                'uuid': plan.uuid,
                'name': plan.name,
                'image': plan.image.url if plan.image else None,
                'startDateandtime': plan.startDateandtime,
                'asistentes': [inv.invited_user.uuid for inv in plan.privateplaninvitation_set.filter(status=1)],
                'created_by_user': True,
                'active':plan.active
            })


        now = timezone.now()
        
        # Asegurate que todos los date_time de eventos son aware:
        #for evento in eventos:
        #    dt = evento['date_time']
        #    if isinstance(dt, str):
        #        dt = parse_datetime(dt)
        #    if dt is not None and timezone.is_naive(dt):
        #        dt = timezone.make_aware(dt, timezone.get_default_timezone())
        #    evento['date_time'] = dt

        #eventos.sort(key=lambda e: (e['startDateandtime'] < now, e['startDateandtime']))
        #eventos_creados.sort(key=lambda e: (e['startDateandtime'] < now, e['startDateandtime']))
        
        
        #rep['eventos'] = eventos
        #rep['eventos_creados'] = eventos_creados

        #print('eventos creados: ', eventos_creados)

       # return rep  
        def safe_datetime(dt):
            if isinstance(dt, str):
                dt = parse_datetime(dt)
            if dt is not None and timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_default_timezone())
            return dt

        # Normaliza todas las fechas
        for lista in (eventos, eventos_creados):
            for e in lista:
                e['startDateandtime'] = safe_datetime(e['startDateandtime'])

        # 🔹 Ordena primero los eventos futuros (más cercanos), luego los pasados (más recientes)
        def sort_key(e):
            dt = e['startDateandtime'] or now
            # eventos futuros → primero, orden ascendente
            if dt >= now:
                return (0, abs((dt - now).total_seconds()))
            # eventos pasados → después, también orden ascendente (más reciente primero)
            else:
                return (1, abs((now - dt).total_seconds()))

        eventos.sort(key=sort_key)
        eventos_creados.sort(key=sort_key)

        rep['eventos'] = eventos
        rep['eventos_creados'] = eventos_creados

        return rep  

class ItemSerializer(serializers.ModelSerializer):
    people_in_charge = UserProfileBasicSerializer(many=True, read_only=True)

    class Meta:
        model = ItemPlan
        fields = '__all__'


class PrivatePlanSerializer(DynamicFieldsModelSerializer):
    invited_users = UserProfileBasicSerializer(many = True, required=False)
    image = serializers.ImageField(required=False, allow_null=True)
    place_name = serializers.CharField(source='place.name', read_only=True)
    creador_image = serializers.SerializerMethodField()
    created_by_user = serializers.SerializerMethodField()
    user_is_invited = serializers.SerializerMethodField()
    items = ItemSerializer(many=True, read_only=True)
    asistentes = serializers.SerializerMethodField()

    class Meta:
        model = PrivatePlan
        fields = '__all__'
    
    def get_creador_image(self, obj):
        user = obj.creador
        if hasattr(user, 'profile') and user.profile.image:
            return user.profile.image.url
        return None

    def get_created_by_user(self, obj):
        # Necessita acces al usuari del context
        request = self.context.get('request', None)
        print(request)
        if request and hasattr(request, 'user'):
            return obj.creador == request.user
        return False
    
    def get_user_is_invited(self, obj):
        request = self.context.get('request')
        print(request)
        if not request or not request.user or request.user.is_anonymous:
            return False

        user_profile = getattr(request.user, 'profile', None)
        print('userprofile')
        print(user_profile)
        if not user_profile:
            return False

        return obj.invited_users.filter(uuid=user_profile.uuid).exists()
    
    def get_asistentes(self, obj):
        # Filtramos invitaciones con status == 1 (Aceptado)
        invitaciones_aceptadas = PrivatePlanInvitation.objects.filter(
            private_plan=obj, status=1
        ).select_related('invited_user')
        
        # Devolvemos los usuarios con status aceptado
        return UserProfileSerializer(
            [inv.invited_user for inv in invitaciones_aceptadas], many=True
        ).data

            
class EntradaBasicSerializer(serializers.ModelSerializer):
    activity_name = serializers.CharField(source='activity.name', read_only=True)
    activity_start = serializers.DateTimeField(source='activity.startDateandtime', read_only=True)
    activity_image = serializers.ImageField(source='activity.image',required=False, allow_null=True)

    class Meta:
        model = EntradasForPlan
        fields = ['titulo','activity_name', 'activity_start', 'precio','activity_image']



class TicketSerializer(DynamicFieldsModelSerializer):
    entrada = EntradaBasicSerializer(read_only=True)
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = '__all__'

    #vull que torni el path relatiu, perquè si ve amb localhost... es complica a frontend
    def get_qr_code(self, obj):
        if obj.qr_code:
            return obj.qr_code.url  
        return None
    

class CampoReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampoReserva
        fields = ['uuid', 'label']


class ReservaFormSerializer(serializers.ModelSerializer):
    campos = CampoReservaSerializer(many=True, read_only=True)
    disponibles = serializers.SerializerMethodField()

    class Meta:
        model = ReservaForm
        fields = [
            'uuid',
            'nombre',
            'actividad',
            'promo',
            'max_disponibilidad',
            'campos',
            'disponibles',
        ]

    def get_disponibles(self, obj):
        return obj.disponibles()
        
class ReservaSerializer(serializers.ModelSerializer):
    reserva_form_nombre = serializers.CharField(source='reserva_form.nombre', read_only=True)
    class Meta:
        model = Reserva
        fields = ['uuid', 'reserva_form_nombre','values', 'created_at']
    
  

class EventTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTemplate
        fields = '__all__'



class BonoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bono
        fields = '__all__'


class PaymentEventsRangesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentEventsRanges
        fields = '__all__'


