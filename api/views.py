import json
from django.shortcuts import render
from geopy.distance import geodesic
from django.core.mail import send_mail
# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Activity, ItemPlan, Place, PrivatePlan, Promo, Tag, UserProfile, User
from .serializers import ActivitySerializer, PlaceSerializer, PrivatePlanSerializer, PromoSerializer, TagSerializer, UserProfileBasicSerializer,UserProfileSerializer
import ast 
from datetime import datetime
from django.utils import timezone



@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'Hello from Django!'})



@api_view(['GET'])
def get_all_places(request):
    # Obtenemos todos los objetos Place
    places = Place.objects.all()
    
    # Si no hay lugares en la base de datos
    if not places:
        return Response({'error': 'No places found'}, status=404)

    # Serializamos los objetos Place y los devolvemos en la respuesta
    serializer = PlaceSerializer(places, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def place_detail(request):

    name = request.query_params.get('name', None)
    if not name:
        return Response({'error': 'No name provided'}, status=400)
    
    try:
        place = Place.objects.get(name=name)
    except Place.DoesNotExist:
        return Response({'error': 'Place not found'}, status=404)

    serializer = PlaceSerializer(place)
    return Response(serializer.data)

@api_view(['GET'])
def activities(request): #hacer doble view
    print(request.user)
    if request.method == 'GET':
        place_uuid = request.query_params.get('place_uuid',None)
        activity_uuid = request.query_params.get('activity_uuid',None)

        if place_uuid:
            try:
                place = Place.objects.get(uuid=place_uuid)
            except Place.DoesNotExist:
                return Response({'error': 'No place found according to your uuid'}, status=404)
                    
            activities = Activity.objects.filter(place__uuid=place_uuid,startDateandtime__gte=timezone.now()).order_by('startDateandtime')
            print(activities)
            
            if not activities.exists:
                return Response({'error': 'No activities found according to the submitted place'}, status=404)

            serializer = ActivitySerializer(activities, many=True, fields=['uuid','name','shortDesc','place_name','image','startDateandtime','tag_detail','gratis','creador_image','asistentes'])
            return Response(serializer.data)
        elif activity_uuid:
                try: 
                    activity = Activity.objects.get(uuid=activity_uuid)
                except Activity.DoesNotExist:
                    return Response({'error': 'No activity found according to your uuid'}, status=404)

                serializer = ActivitySerializer(activity,context={'request': request})
                return Response(serializer.data)
        else:
            return Response({'error':'Neither place or activity submitted'},status=404)
    
        
    
@api_view(['GET','POST'])
def promos(request):

    if request.method == 'GET': 
        
        #promos = Promo.objects.all()

        #promoser = PromoSerializer(promos, many=True)

        #return Response(promoser.data)

        place_uuid = request.query_params.get('place_uuid',None)
        promo_uuid = request.query_params.get('promo_uuid',None)

        if place_uuid:
            try:
                place = Place.objects.get(uuid=place_uuid)
            except Place.DoesNotExist:
                return Response({'error': 'No place found according to your uuid'}, status=404)
                    
            promos = Promo.objects.filter(place__uuid=place_uuid).order_by('startDateandtime')
            
            if not promos.exists:
                return Response({'error': 'No promos found according to the submitted place'}, status=404)

            serializer = PromoSerializer(promos, many=True, fields=['uuid','name','shortDesc','place_name','image','startDateandtime','endDateandtime','tag_detail','creador_image','asistentes'])
            print(serializer)
            return Response(serializer.data)
        elif promo_uuid:
                try: 
                    promo =  Promo.objects.get(uuid=promo_uuid)
                except Promo.DoesNotExist:
                    return Response({'error': 'No promo found according to your uuid'}, status=404)

                serializer = PromoSerializer(promo)
                return Response(serializer.data)
        else:
            return Response({'error':'Neither place or activity submitted'},status=404)

    

    

@api_view(['GET'])
def tags(request): 

    #GET ALL TAGS
    tags = Tag.objects.all()
    
    # Si no hay lugares en la base de datos
    if not tags:
        return Response({'error': 'No tags found'}, status=404)

    # Serializamos los objetos Place y los devolvemos en la respuesta
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def user_profile(request):

    if not request.user.is_authenticated:
        return Response({'error': 'User is not authenticated'}, status=404)
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=404)
    

    serializer = UserProfileSerializer(user_profile, context={'request': request})

    return Response(serializer.data)


@api_view(['POST'])
def user_prorfile_from_uuid(request):
    user_uuid = request.data['user_uuid']
    print(user_uuid)
    try:
        user = UserProfile.objects.get(uuid=user_uuid)
    except UserProfile.DoesNotExist:
        return Response('Not such userprofile', status = 404)

    serializer = UserProfileSerializer(user, context={'request': request})
    return Response(serializer.data) 



@api_view(['POST'])
def update_user(request):

    print(request.data)
    
    data = request.data.copy()
    user_uuid = data['user_uuid']
    try:
        user = UserProfile.objects.get(uuid=user_uuid)

        if 'description' in data:
            user.bio = data['description']

        if 'birthday_date' in data:
            birth_date_str = data['birthday_date']
            try:
                birth_date = datetime.strptime(birth_date_str, "%Y/%m/%d").date()
            
            except ValueError:
                return Response("Fecha inválida. Usa el formato DD/MM/YYYY.", status=400)

            user.birth_date = birth_date

        if 'place_location' in data:
            user.originLocation = data['place_location']
            user.originLocationId = data['place_location_id']

        if 'tags' in data:
        # Parsear la lista de tags correctamente
            tags_raw = request.data.get('tags', '[]')
            try:
                tags_list = ast.literal_eval(tags_raw)
                if not isinstance(tags_list, list):
                    tags_list = []
            except (ValueError, SyntaxError):
                tags_list = []
            print(tags_list)
            user.tags.set(tags_list)
        
        if 'image' in data:
            user.image = data['image']
        user.save()
        return Response({'user_uuid': user.uuid}, status=200)

    except UserProfile.DoesNotExist:
        return Response('No such UserProfile exists', status=404)
    
def find_nearest_place(lat, lng):
    all_places = Place.objects.all()
    for place in all_places:
        dist = geodesic((lat, lng), (place.latitude, place.longitude)).km
        if dist < 50:  #radio de 50km
            return place

    return None

@api_view(['POST'])
def sign_in(request):

    data = request.data

    if User.objects.filter(email=data['email']).exists():
        return Response({"error":"Este mail ya está en uso para un usuario"},status=404)
    
    user = User.objects.create_user(
            username=data['name'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('name', '')
        )
    userProfile = UserProfile.objects.create(user=user)

    print(userProfile.uuid)
    refresh = RefreshToken.for_user(user)
    return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_uuid':str(userProfile.uuid)
        })

@api_view(['POST'])
def google_sign_in(request):
    id_token = request.data.get('idToken')
    if not id_token:
        return Response({"error": "Token requerido"}, status=400)
    response = request.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}")
    if response.status_code != 200:
        return Response({"error": "Token inválido"}, status=400)

    payload = response.json()
    email = payload['email']
    name = payload.get('name', '')

    user, created = User.objects.get_or_create(
        email=email,
        defaults={'username': email, 'first_name': name}
    )
    userProfile = UserProfile.objects.create(user=user)
    refresh = RefreshToken.for_user(user)
    return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


@api_view(['POST'])
def updateActivityAssistance(request):

    data = request.data

    user = request.user
    activity_uuid = data.get('activity_uuid')
    promo_uuid = data.get('promo_uuid')


    if activity_uuid:
        try:
            activity = Activity.objects.get(uuid=activity_uuid)
            try:
                update_value = int(data['update'])
                try:
                        userProfile = UserProfile.objects.get(user=user)
                        if userProfile:
                            if update_value == 1 : 
                                userProfile.activities.add(activity)
                            elif update_value == -1:
                                userProfile.activities.remove(activity)

                except UserProfile.DoesNotExist:
                    return Response('Error in access token', status = 404)
                
            except (ValueError, TypeError):
                return Response({'error': 'update must be an integer'}, status=400)
            
            asistentes = UserProfile.objects.filter(activities=activity)
            serializer = UserProfileBasicSerializer(asistentes, many=True, context={"request": request})

            return Response(serializer.data, status=200)


        except Activity.DoesNotExist:
            return Response({'error': 'Activity not found'}, status=404)
    elif promo_uuid:
        try:
            promo = Promo.objects.get(uuid=promo_uuid)
            try:
                update_value = int(data['update'])
                try:
                    userProfile = UserProfile.objects.get(user=user)
                    if userProfile:
                        if update_value == 1 : 
                            userProfile.promos.add(promo)
                        elif update_value == -1:
                            userProfile.promos.remove(promo)

                except UserProfile.DoesNotExist:
                    return Response('Error in access token', status = 404)
            except (ValueError, TypeError):
                return Response({'error': 'update must be an integer'}, status=400)
            print(promo.asistentes)

            promo.asistentes = promo.asistentes + update_value
            
            print(promo.asistentes)

            promo.save()

            return Response({'asistentes': promo.asistentes}, status=200)


        except Promo.DoesNotExist:
            return Response({'error': 'Activity not found'}, status=404)


@api_view(['POST'])
def create_event(request):
    data = request.data.copy()
    lat = request.data.get('lat')
    lng = request.data.get('long')
    nearest_place = find_nearest_place(lat, lng)
    name = request.data.get('name')
    
    if data['isPrivatePlan'] == 'false':
        # Parsear la lista de tags correctamente
        tags_raw = request.data.get('tags', '[]')
        try:
            tags_list = ast.literal_eval(tags_raw)
            if not isinstance(tags_list, list):
                    tags_list = []
        except (ValueError, SyntaxError):
            tags_list = []
            
        del data['tags'] #ho borrem del serializer d'Activity i els passarem després
    data['gratis'] = bool(request.data.get('gratis'))
    data['price'] = float(request.data.get('price'))
    data['lat'] = float(request.data.get('lat'))
    data['long'] = float(request.data.get('long'))
        
    if not nearest_place:
            ##send_mail(
            ##    'Nueva actividad sin lugar asociado!',
            ##   f'Se creó una actividad sin place. Coordenadas: {lat}, {lng}. El nombre de la actividad es:{name}',
            ##    'rebuig.lauragonzalez@gmail.com',
            ##    ['lauragonzalezcomalada@gmail.com'],
            ##    fail_silently=False,
            ##)
        print('not nearest place')
        data['place'] = None
    else:
        data['place'] = nearest_place.id

    print(data['isPlan'])
    print(data['isPromo'])
    print(data['isPrivatePlan'])
    if data['isPlan'] == 'true':
        serializer = ActivitySerializer(data=data)
    elif data['isPromo'] == 'true':
        serializer = PromoSerializer(data=data)
    else: #data['isPrivatePlan] == 'true
        serializer = PrivatePlanSerializer(data=data)

    if serializer.is_valid():
        event = serializer.save()
        if data['isPrivatePlan'] == 'false':
            if tags_list:
                event.tags.set(tags_list)
        event.creador = request.user
        event.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
def search_users(request):

    query = request.GET.get('query', '')
    results = UserProfile.objects.filter(user__username__icontains=query)[:10]

    serializer = UserProfileSerializer(results, many=True, fields=['uuid','username'] )
    return Response(serializer.data, status = 200)


@api_view(['GET'])
def private_plans(request):

    user = request.user
    privatePlanUuid = request.GET.get('privatePlanUuid','')

    print(privatePlanUuid)
    print(type(user))
    #Generic per tenir els privatePlans d'un user
    if not privatePlanUuid:
        try:
            userProfile = UserProfile.objects.get(user = user)
        except UserProfile.DoesNotExist:
            return Response(status = 404)   

        print(userProfile.planes_invitados.all())
        
        serializer = PrivatePlanSerializer(userProfile.planes_invitados.all(), many=True)
    # return Response(UserProfileSerializer(userProfile).data, status = 200)
        return Response(serializer.data, status = 200)
    
    #Per tenir el detall d'un privatePlan
    else:
        try:
            privatePlan = PrivatePlan.objects.get(uuid=privatePlanUuid, invited_users__user = user)
        except PrivatePlan.DoesNotExist:
            return Response('No hay tal plan para tal usuario',status = 404)
        
        serializer = PrivatePlanSerializer(privatePlan)
        return Response(serializer.data, status = 200)
    
@api_view(['POST'])
def update_item_details(request):

    data = request.data.copy()
    item_uuid = data['uuid']
    private_plan_uuid = data['plan_uuid']
    amount = data['newAssignedAmountValue']

    try:

        item = ItemPlan.objects.get(uuid=item_uuid, private_plan__uuid=private_plan_uuid)
    
    except ItemPlan.DoesNotExist:
        return Response('No hay tal plan')
    

    item.assignedAmount = float(amount)
    item.save()

    return Response(item.assignedAmount, status = 200)