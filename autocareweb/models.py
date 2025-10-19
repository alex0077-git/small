from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class UserRole(models.TextChoices):
    ADMIN = 'admin', _('Admin')
    SERVICE_MANAGER = 'service_manager', _('ServiceManager')
    MECHANIC = 'mechanic', _('Mechanic')
    CUSTOMER = 'customer', _('Customer')

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CUSTOMER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class UserDetails(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='details')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=50)
    place = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return self.name

####//////////Vehicle details/////////////////    
VEHICLE_TYPE_CHOICES = [
    ('car', 'Car'),
    ('bike', 'Bike'),
]

class VehicleMake(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='vehicle_make_images/', blank=True, null=True)

    def __str__(self):  
        return self.name

class VehicleModel(models.Model):
    make = models.ForeignKey(VehicleMake, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=100)
    year = models.IntegerField()
    image = models.ImageField(upload_to='vehicle_model_images/', blank=True, null=True)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES)

    def _str_(self):
        return f"{self.make.name} {self.model_name} ({self.year}) - {self.get_vehicle_type_display()}"
    


class Vehicle(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE)
    registration_number = models.CharField(max_length=20, unique=True)



#////////////////Service Lists//////////////



class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='service_category_images/', blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return self.name
    




class ServiceType(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ServiceCategory, related_name='service_types', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='service_type_images/', blank=True, null=True)
    description = models.TextField()
    service_time= models.IntegerField(default=60)
    def __str__(self):
        return self.name


class ServicePrice(models.Model):
    service_type = models.ForeignKey(ServiceType, related_name='service_prices', on_delete=models.CASCADE)
    vehicle_model = models.ForeignKey(VehicleModel, related_name='service_prices', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def _str_(self):
        return f"{self.service_type.name} for {self.vehicle_model} - ₹{self.price} INR"
    

#///////////////// Service cart ///////////////////////////
from django.utils import timezone
class ServiceCart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # User who owns the cart
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)  # Service type added to the cart
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)  # Selected vehicle
    cart_date = models.DateTimeField(default=timezone.now) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart: {self.user.email} - {self.service_type.name} for {self.vehicle.registration_number}"
    

#//////// Order Service ///////////////////////////////////////////

from django.db import models
from django.utils import timezone

# class Order(models.Model):
#     ORDER_STATUS = [
#         ('pending', 'Pending'),
#         ('completed', 'Completed'),
#         ('confirmed', 'Confirmed'),
#     ]
    
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # User who placed the order
#     vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)  # Vehicle selected for the order
#     order_id = models.CharField(max_length=20, unique=True)  # Unique order identifier
#     order_date = models.DateTimeField(default=timezone.now)  # Date when the order was placed
#     status = models.CharField(max_length=10, choices=ORDER_STATUS, default='pending')  # Order status
    
#     def __str__(self):
#         return f"Order {self.order_id} by {self.user.email} for {self.vehicle.registration_number}"


# class Order(models.Model):
#     ORDER_STATUS = [
#         ('pending', 'Work in Progress'),
#         ('completed', 'Completed'),
#         ('confirmed', 'Order Confirmed'),
#     ]
    
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
#     order_id = models.CharField(max_length=20, unique=True)
#     order_date = models.DateTimeField(default=timezone.now)
#     service_date = models.DateField(null=True, blank=True) # New field for the selected service date
#     status = models.CharField(max_length=10, choices=ORDER_STATUS, default='confirmed')

#     def __str__(self):
#         return f"Order {self.order_id} by {self.user.email} for {self.vehicle.registration_number}"

#//////////////////////////  slot list ////////////////////////

class SlotStatus(models.TextChoices):
    ALLOCATED = 'allocated', _('Allocated')
    FREE = 'free', _('Free')
    DISABLED = 'disabled', _('Disabled')

class Slot(models.Model):
    slotname = models.CharField(max_length=100)
    mechanic = models.ForeignKey(CustomUser, limit_choices_to={'role': 'mechanic'}, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=10, choices=SlotStatus.choices, default=SlotStatus.FREE)
    slug = models.SlugField(unique=True, blank=True)

    

class AllocatedManager(models.Model):
    manager = models.ForeignKey(
        CustomUser,
        limit_choices_to={'role': UserRole.SERVICE_MANAGER},
        on_delete=models.CASCADE
    )
    slot = models.ForeignKey(
        Slot,
        on_delete=models.CASCADE
    )



class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Work in Progress'),
        ('completed', 'Completed'),
        ('confirmed', 'Order Confirmed'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=20, unique=True)
    order_date = models.DateTimeField(default=timezone.now)
    service_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default='confirmed')
    allocated_slot = models.ForeignKey(Slot, null=True, blank=True, on_delete=models.SET_NULL)  # ForeignKey to Slot model

    def __str__(self):
        return f"Order {self.order_id} by {self.user.email} for {self.vehicle.registration_number}"

    def allocate_slot(self):
        # Get the first available free slot
        free_slot = Slot.objects.filter(status=SlotStatus.FREE).first()
        if free_slot:
            free_slot.status = SlotStatus.ALLOCATED
            free_slot.save()  # Update slot status to allocated
            self.allocated_slot = free_slot  # Assign slot to the order
        else:
            raise ValueError("No free slots available")

    def save(self, *args, **kwargs):
        if not self.allocated_slot:
            self.allocate_slot()  # Automatically allocate a slot when saving
        super().save(*args, **kwargs)


class OrderService(models.Model):
    order = models.ForeignKey(Order, related_name='services', on_delete=models.CASCADE)  # The order this service belongs to
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)  # The service being ordered
    price = models.DecimalField(max_digits=10, decimal_places=2)  # The price of the service

    def __str__(self):
        return f"{self.service_type.name} for order {self.order.order_id}"





#//////////////////////////  slot list ////////////////////////



class AllocatedMechanic(models.Model):
    mechanic = models.ForeignKey(
        CustomUser,
        limit_choices_to={'role': UserRole.MECHANIC},
        on_delete=models.CASCADE,
        related_name='allocated_mechanics'  # Unique reverse accessor for mechanic
    )
    manager = models.ForeignKey(
        CustomUser,
        limit_choices_to={'role': UserRole.SERVICE_MANAGER},
        on_delete=models.CASCADE,
        related_name='allocated_managers'  # Unique reverse accessor for manager
    )
    slot = models.ForeignKey(
        Slot,
        on_delete=models.CASCADE
    )
    allocated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('slot', 'mechanic')  # To prevent multiple mechanics being assigned to one slot

    def __str__(self):
        return f"Mechanic {self.mechanic.email} assigned to Slot {self.slot.slotname}"


class AllocateJuniorMechanics(models.Model):
    junior_mechanic = models.ForeignKey(
        CustomUser,
        limit_choices_to={'role': UserRole.MECHANIC},
        on_delete=models.CASCADE,
        related_name='allocated_junior_mechanics'  # This is correct
    )
    senior_mechanic = models.ForeignKey(
        CustomUser,
        limit_choices_to={'role': UserRole.MECHANIC},
        on_delete=models.CASCADE,
        related_name='allocating_senior_mechanics'  # This is correct
    )
    service_manager = models.ForeignKey(
        CustomUser,
        limit_choices_to={'role': UserRole.SERVICE_MANAGER},
        on_delete=models.CASCADE,
        related_name='junior_mechanic_allocations'  # This is correct
    )
    slot = models.ForeignKey(
        Slot,
        on_delete=models.CASCADE
    )
    allocated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Junior Mechanic {self.junior_mechanic.email} allocated by Senior Mechanic {self.senior_mechanic.email} for Slot {self.slot.slotname}"




from django.db import models
from django.utils.translation import gettext_lazy as _


class MechanicLevel(models.IntegerChoices):
    SENIOR = 1, _('Senior Level')
    MEDIUM = 2, _('Medium Level')
    ENTRY = 3, _('Entry Level')

class MechanicStatus(models.IntegerChoices):
    WORKING = 1, _('Working')
    ACTIVE = 2, _('Active')
    ABSENTEES = 3, _('Absentees')

class Mechanic(models.Model):
    mechanic = models.OneToOneField(CustomUser, on_delete=models.CASCADE, default=1)
    status = models.IntegerField(choices=MechanicStatus.choices, default=MechanicStatus.ACTIVE)
    level = models.IntegerField(choices=MechanicLevel.choices, default=MechanicLevel.ENTRY)

    def __str__(self):
        return f"{self.mechanic.email} - {self.get_level_display()}"
    
    


class CustomerComplaint(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='complaints')
    complaint = models.TextField()

    def __str__(self):
        return f"Complaint from {self.user.details.name} ({self.user.email})"
    
#/////////////////////  Job portal ////////////////////////

from django.db import models
from django.contrib.auth import get_user_model

class JobPost(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    company_name = models.CharField(max_length=255)
    posted_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  # Mechanics post the job
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class JobApplication(models.Model):
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    candidate_name = models.CharField(max_length=255)
    candidate_email = models.EmailField()
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)
    is_selected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.candidate_name} - {self.job.title}"