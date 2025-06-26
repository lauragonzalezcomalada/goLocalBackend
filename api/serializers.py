from operator import itemgetter
from rest_framework import serializers
from .models import Place, Activity, PrivatePlan, Promo,Tag,UserProfile, ItemPlan


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

 

class ActivitySerializer(DynamicFieldsModelSerializer):
    
    place_name = serializers.CharField(source='place.name', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    asistentes = UserProfileBasicSerializer(many=True, read_only=True, source='activities')  # Este es el campo nuevo

    tag_detail = TagSerializer(required=False, many=True,read_only=True, source='tags') #para el GET, que se muestra todo el Tag
    creador_image = serializers.SerializerMethodField()
    created_by_user = serializers.SerializerMethodField()

    user_isgoing = serializers.SerializerMethodField()
    class Meta:
        model = Activity
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
            return obj.creador == request.user
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

class PromoSerializer(DynamicFieldsModelSerializer):

    place_name = serializers.CharField(source='place.name', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    tag_detail = TagSerializer(required=False, many=True,read_only=True, source='tags') #para el GET, que se muestra todo el Tag

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
            return obj.creador == request.user
        return False



class UserProfileSerializer(DynamicFieldsModelSerializer):
    tags = TagSerializer(many=True)
    username = serializers.CharField(source='user.username', read_only=True)  # Nombre de usuario
    activity_detail = ActivitySerializer(required=False, many=True,read_only=True, source='activities')

    class Meta:
        model = UserProfile
        fields = ['uuid','username','bio','tags','birth_date','creation_date','image','rate','originLocation','activity_detail']

    def to_representation(self, instance):
        # Aseguramos pasar el contexto con request
        rep = super().to_representation(instance)
        rep['activities'] = ActivitySerializer(
            instance.activities.all(), 
            many=True, 
            context=self.context  # <== esto es clave
        ).data
        return rep

class ItemSerializer(serializers.ModelSerializer):
    people_in_charge = UserProfileBasicSerializer(many=True, read_only=True)

    class Meta:
        model = ItemPlan
        fields = '__all__'

class PrivatePlanSerializer(DynamicFieldsModelSerializer):
    invited_users = UserProfileBasicSerializer(many = True)
    image = serializers.ImageField(required=False, allow_null=True)
    place_name = serializers.CharField(source='place.name', read_only=True)
    creador_image = serializers.SerializerMethodField()
    created_by_user = serializers.SerializerMethodField()

    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = PrivatePlan
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
            return obj.creador == request.user
        return False
    
