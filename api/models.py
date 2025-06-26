import random
import string
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
# api/models.py

class Place(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100)
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
    image = models.ImageField(upload_to='activities_images/', null=True, blank=True)
    startDateandtime = models.DateTimeField(null=True, blank=True)
    instagram_link = models.CharField(max_length=100, null=True, blank=True)
    web_link = models.CharField(max_length=100, null = True, blank=True)
    tickets_link = models.CharField(max_length=100, null=True, blank=True)
    gratis = models.BooleanField(default=True)
    reserva_necesaria =  models.BooleanField(default=True)
    price = models.FloatField(default = 0.0)
    tags = models.ManyToManyField(Tag, blank=True, related_name='activities')
    creador = models.ForeignKey(User, on_delete=models.CASCADE, default = 1)

   # asistentes = models.IntegerField(default = 0,validators=[MinValueValidator(0)])
    
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
    image = models.ImageField(upload_to='promo_images/', null=True, blank=True)
    startDateandtime = models.DateTimeField(null=True, blank=True)
    endDateandtime = models.DateTimeField(null=True, blank=True)
    repeat = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True, related_name='promos')
    creador = models.ForeignKey(User, on_delete=models.CASCADE, default = 1)
    asistentes = models.IntegerField(default = 0)

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
    image = models.ImageField(upload_to='private_plans_images/', null=True, blank=True)
    startDateandtime = models.DateTimeField(null=True, blank=True)
    creador = models.ForeignKey(User, on_delete=models.CASCADE, default = 1)
    gratis = models.BooleanField(default=True)
    reserva_necesaria =  models.BooleanField(default=True)
    price = models.FloatField(default = 0.0)
    invitation_code = models.CharField(max_length=8, unique=True, blank=True, null=True)
    invited_users = models.ManyToManyField('UserProfile', through='PrivatePlanInvitation', related_name='planes_invitados', blank=True)
    

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


class UserProfile(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    originLocation = models.CharField(max_length=256, blank=True, null=True)
    originLocationId = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='profiles_images/', null=True, blank=True)
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
