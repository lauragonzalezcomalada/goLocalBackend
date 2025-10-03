from datetime import timezone
from decimal import Decimal
import random
import string
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone
from cloudinary.models import CloudinaryField as ImageField


# Create your models here.
# api/models.py

class Place(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=110)
    desc = models.CharField(max_length = 256)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='places_images/', null=True, blank=True)


    def __str__(self):
        return self.name
    

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=100, default='fa-star')

    def __str__(self):
        return self.name
    
    
class Activity(models.Model):
    
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100)
    shortDesc = models.CharField(max_length = 144, null=True, blank = True)
    desc = models.TextField(blank = True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='activities',null=True,blank=True)
    lat = models.FloatField(null=True)
    long = models.FloatField(null=True)
    direccion = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='activities_images/', null=True, blank=True)
    startDateandtime = models.DateTimeField(null=True, blank=True)
    tickets_link = models.CharField(max_length=100, null=True, blank=True)
    gratis = models.BooleanField(default=True)
    reserva_necesaria =  models.BooleanField(default=False, blank = True, null = True)
    control_entradas =  models.BooleanField(default=False, blank = True, null = True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='activities')
    creador = models.ForeignKey(User, on_delete=models.CASCADE, default = 1)
    price = models.FloatField(default = 0.0,validators=[MinValueValidator(0.0)])
    views = models.IntegerField(default = 0,validators=[MinValueValidator(0)])
    shares = models.IntegerField(default = 0,validators=[MinValueValidator(0)])
    clicks_on_tickets_link = models.IntegerField(default = 0,validators=[MinValueValidator(0)])
    active = models.BooleanField(default=False)
    colaboradores = models.ManyToManyField('UserProfile', related_name='activities_collaborated', blank=True)


    def __str__(self):
        return self.name
    
class Promo(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100)
    shortDesc = models.CharField(max_length = 144, null=True, blank = True)
    desc = models.TextField(blank = True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='promos',null=True,blank=True)
    lat = models.FloatField(null=True)
    long = models.FloatField(null=True)
    direccion = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='promo_images/', null=True, blank=True)
    startDateandtime = models.DateTimeField(null=True, blank=True)
    endDateandtime = models.DateTimeField(null=True, blank=True)
    repeat = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True, related_name='promos')
    creador = models.ForeignKey(User, on_delete=models.CASCADE, default = 1)
    reserva_necesaria =  models.BooleanField(default=False, blank = True, null = True)
    views = models.IntegerField(default = 0,validators=[MinValueValidator(0)])
    shares = models.IntegerField(default = 0,validators=[MinValueValidator(0)])
    active = models.BooleanField(default=False)
    colaboradores = models.ManyToManyField('UserProfile', related_name='promos_collaborated', blank=True)




    def __str__(self):
        return self.name


def generate_invitation_code(length=8):
    chars = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))
        if not PrivatePlan.objects.filter(invitation_code=code).exists():
            return code
        
class PrivatePlan(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100)
    shortDesc = models.CharField(max_length = 144, null=True, blank = True)
    desc = models.TextField(blank = True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='private_plans',null=True,blank=True)
    lat = models.FloatField(null=True)
    long = models.FloatField(null=True)
    direccion = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='private_plans_images/', null=True, blank=True)
    startDateandtime = models.DateTimeField(null=True, blank=True)
    creador = models.ForeignKey(User, on_delete=models.CASCADE, default = 1)
    gratis = models.BooleanField(default=True)
    reserva_necesaria =  models.BooleanField(default=True)
    price = models.FloatField(default = 0.0)
    invitation_code = models.CharField(max_length=8, unique=True, blank=True, null=True)
    invited_users = models.ManyToManyField('UserProfile', through='PrivatePlanInvitation', related_name='planes_invitados', blank=True, null = True)
    active = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if not self.invitation_code:
            self.invitation_code = generate_invitation_code()
        super().save(*args, **kwargs)


class PrivatePlanInvitation(models.Model):
    private_plan = models.ForeignKey(PrivatePlan, on_delete=models.CASCADE)
    invited_user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)

    STATUS_CHOICES = [
        (0, 'Invitado'),
        (1, 'Aceptado'),
        (2, 'Pagado'),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    class Meta:
        unique_together = ('private_plan', 'invited_user')

class ItemPlan(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique = True)
    name = models.CharField(max_length=100)
    neededAmount = models.FloatField(default = 0.0)
    assignedAmount = models.FloatField(default = 0.0)
    people_in_charge = models.ManyToManyField(
            'UserProfile',
            related_name='items_in_charge'
        )
    private_plan = models.ForeignKey(
            PrivatePlan,
        on_delete=models.CASCADE,
        related_name='items'  # te permite hacer plan.items.all()
    )



class PaymentEventsRanges(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    name = models.CharField(max_length=100)
    start_range = models.PositiveIntegerField()
    end_range = models.PositiveIntegerField(null=True, blank=True)
    price =  models.FloatField(default = 0.0,validators=[MinValueValidator(0.0)])

class UserProfile(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=256, blank=True, null=True)
    locationId = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='profiles_images/', null=True, blank=True,max_length=255)
    rate = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='users')
    activities = models.ManyToManyField(Activity, blank = True,related_name='activities')
    promos = models.ManyToManyField(Promo,blank = True, related_name='promos')
    siguiendo = models.ManyToManyField('self', symmetrical=False, related_name='seguidores', blank=True)
    telefono = models.IntegerField(null = True, blank = True)
    available_planes_gratis = models.IntegerField(default=4, null=True, blank = True)
    payment_events_range = models.OneToOneField(
        PaymentEventsRanges,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profiles"
    )
    creador = models.BooleanField(default=False)
    pago_suscripcion_mes_proximo = models.BooleanField(default=False)
    pago_suscripcion_mes_actual = models.BooleanField(default=False)
    mp_access_token = models.TextField(null=True, blank=True)
    mp_refresh_token = models.TextField(null=True, blank=True)
    mp_user_id = models.BigIntegerField(null=True, blank=True)
    token_expiration = models.DateTimeField(null=True, blank=True)
    platform_fee = models.DecimalField(
    max_digits=3,       #i.e. 12.5% no 12.45%
    decimal_places=1,  
    default=Decimal("12.5")
)


class EntradasForPlan(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='entradas_for_plan', null=True, blank=True)
    promo = models.ForeignKey(Promo, on_delete=models.CASCADE, related_name='entradas_for_promo', null=True, blank=True)
    privateplan = models.ForeignKey(PrivatePlan, on_delete=models.CASCADE, related_name='entradas_for_plan_privado', null=True, blank=True)
    maxima_disponibilidad = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    disponibles = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    precio = models.FloatField(default=0.0)
    titulo =  models.TextField(blank=False)
    desc = models.TextField(blank=True)

    #mètode perquè es guardi el valor de disponibles com al de màxima_disponibilitat quan es crea per primer cop
    def save(self, *args, **kwargs):
        if self._state.adding and self.disponibles == 0 and self.maxima_disponibilidad > 0:
            self.disponibles = self.maxima_disponibilidad
        super().save(*args, **kwargs)




class Ticket(models.Model):
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    entrada = models.ForeignKey(EntradasForPlan, on_delete=models.CASCADE, related_name="tickets",null=True, blank=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fecha_compra = models.DateTimeField(default=timezone.now)
    precio = models.FloatField(default=0.0, null=True, blank = True)
    
    STATUS_CHOICES = [
        (0, 'No asistido'),
        (1, 'Asistido'),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return f"Entrada de {self.user_profile} tipo {self.entrada.titulo} ({self.uuid})"


    def generate_qr_code(self):
        qr_data = f"http://192.168.1.39:8000/api/validate_ticket?ticket={self.uuid}"
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        filename = f"qr_{self.uuid}.png"
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        # Genera el QR antes de guardar
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)
class CampoReserva(models.Model):
    TIPO_CHOICES = [
        ('text', 'Texto'),
        ('email', 'Email'),
        ('number', 'Número'),
        ('date', 'Fecha'),
    ]
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    nombre = models.CharField(max_length=100)  # 'email', 'nombre', etc.
    label = models.CharField(max_length=100)   # lo que se muestra en el form
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    requerido = models.BooleanField(default=False)
class ReservaForm(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    nombre = models.CharField(max_length=100)  # ej: "Interior", "Terraza", "VIP"
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='reservas_forms', null=True, blank=True)
    promo = models.ForeignKey(Promo, on_delete=models.CASCADE, related_name='reservas_forms', null=True, blank=True)
    max_disponibilidad = models.PositiveIntegerField()
    campos = models.ManyToManyField('CampoReserva', related_name='formularios', blank=True)
    confirmados = models.PositiveIntegerField(default = 0)


    def disponibles(self):
        # método para calcular disponibilidad restante
        return self.max_disponibilidad - self.reservas.count()




class Reserva(models.Model):

    STATUS_CHOICES = [
        (0, 'No asistido'),
        (1, 'Asistido')
    ]
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    reserva_form = models.ForeignKey(ReservaForm, on_delete=models.CASCADE, related_name='reservas', null=True, blank=True)
    values = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    estado = models.IntegerField(choices=STATUS_CHOICES, default=0)


class EventTemplate(models.Model):

    TIPO_EVENT_CHOICES = [
        (0, 'Activity'),
        (1, 'Promo'),
        (2,'Plan Privado')
    ]
     
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    name = models.CharField(max_length=100)
    tipoEvento = models.IntegerField(choices=TIPO_EVENT_CHOICES, default=0)
    values = models.JSONField()
    creador = models.ForeignKey(User, on_delete=models.CASCADE, default = 1)



class Bono(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    name = models.CharField(max_length=100)
    amount = models.PositiveIntegerField()
    price =  models.FloatField(default = 0.0,validators=[MinValueValidator(0.0)])

class Payment(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True, blank = True)
    userProfile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="payments") # el qui paga
    
    # Datos del pago
    payment_id = models.CharField(max_length=50, unique=True, null=True, blank=True)  # ID de MP
    status = models.CharField(max_length=20)  # status del client a MP: approved, pending, rejected, refunded
    total_amount = models.DecimalField(max_digits=10, decimal_places=2) # quantitat total
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2) # quantitat per mi
    seller_amount = models.DecimalField(max_digits=10, decimal_places=2) # quantitat pel seller
    
    # Info de negocio
    descripcion = models.CharField(max_length=200, null=True, blank = True) # descripció de xq es el payment
    seller = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="incoming_payments") #pk
    activity = models.ForeignKey(Activity,on_delete=models.CASCADE, related_name="payments", null=True, blank=True ) #pk o null si es transacció interna
    event_type = models.CharField(max_length=20)  # activity, promo, plan, etc.
    
    # Metadata adicional y tracking
    metadata = models.JSONField(default=dict, null=True, blank = True) # per store el que em torna MP, per si hi han errors
    payout_status = models.CharField(max_length=20, default='pending')  # status de jo pagat al seller
    created_at = models.DateTimeField(auto_now_add=True) # quan es crea payment
    updated_at = models.DateTimeField(auto_now=True) # quan s'actualitza, de status...

    applied = models.BooleanField(null=False, blank = False, default = False) # bool de si s'executa el que es necessiti, crear tickets, extendre els bonos, range...

    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}" 


class MessageToUser(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    dateTime = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank = False, null = False)
    userProfile = models.ManyToManyField(
            'UserProfile',
            related_name='messages'
        )
    read =  models.BooleanField(default=False)
