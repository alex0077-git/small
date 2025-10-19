from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'role', 'password1', 'password2')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email')

class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = UserDetails
        fields = ['name', 'phone', 'address', 'city', 'place', 'pincode']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }

# class VehicleForm(forms.ModelForm):
#     class Meta:
#         model = Vehicle
#         fields = ['vehicle_type', 'vehicle_brand', 'vehicle_variant', 'vehicle_number']
#         widgets = {
#             'vehicle_type': forms.Select(attrs={'id': 'vehicleType', 'required': True}),
#             'vehicle_brand': forms.Select(attrs={'id': 'vehicleBrand', 'required': True}),
#             'vehicle_variant': forms.TextInput(attrs={'id': 'vehicleVariant', 'required': True}),
#             'vehicle_number': forms.TextInput(attrs={'id': 'vehicleNumber', 'required': True}),
#         }


from .models import VehicleMake, VehicleModel

class VehicleMakeForm(forms.ModelForm):
    class Meta:
        model = VehicleMake
        fields = ['name', 'image']  # Define the fields to include in the form

class VehicleModelForm(forms.ModelForm):
    class Meta:
        model = VehicleModel
        fields = ['model_name', 'year', 'image', 'vehicle_type'] 

        # Customize widgets (optional) for better rendering
        widgets = {
            'vehicle_type': forms.RadioSelect,  # To show radio buttons for vehicle type choices
        }



# class SlotForm(forms.ModelForm):
#     class Meta:
#         model = Slot
#         fields = ['slotname', 'mechanic', 'status']

# class SlotForm(forms.ModelForm):
#     class Meta:
#         model = Slot
#         fields = ['slotname', 'status', 'mechanic']  # Keep the mechanic field for now

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Limit the mechanic field queryset to service managers instead of mechanics
#         self.fields['mechanic'].queryset = CustomUser.objects.filter(role=UserRole.SERVICE_MANAGER)
#         self.fields['mechanic'].label = "Service Manager"  # Change the label to reflect this is for managers





class AllocateManagerForm(forms.ModelForm):
    class Meta:
        model = AllocatedManager
        fields = ['manager']  # Only the manager field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit the queryset to only service managers
        self.fields['manager'].queryset = CustomUser.objects.filter(role=UserRole.SERVICE_MANAGER)



class SlotForm(forms.ModelForm):
    manager = forms.ModelChoiceField(queryset=CustomUser.objects.filter(role=UserRole.SERVICE_MANAGER), label="Service Manager")

    class Meta:
        model = Slot
        fields = ['slotname', 'status']

    def save(self, commit=True):
        # Save the slot first
        slot = super().save(commit=False)

        # Save the slot instance
        if commit:
            slot.save()

        # Handle the allocated manager assignment
        manager = self.cleaned_data.get('manager')
        if manager:
            AllocatedManager.objects.update_or_create(
                slot=slot,
                defaults={'manager': manager}
            )
        return slot
class ManagerAllocationForm(forms.Form):
    manager = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role=UserRole.SERVICE_MANAGER),
        label="Service Manager",
        required=True
    )


# class AssignMechanicForm(forms.Form):
#     slot_id = forms.CharField(widget=forms.HiddenInput())  # Hidden field to store the slot ID
#     mechanic = forms.ModelChoiceField(
#         queryset=CustomUser.objects.filter(role=UserRole.MECHANIC),
#         label="Select Mechanic"
#     )
class AssignMechanicForm(forms.Form):
    mechanic = forms.ModelChoiceField(
        queryset=Mechanic.objects.filter(level=MechanicLevel.SENIOR, status=MechanicStatus.ACTIVE),
        required=True
    )
    slot_id = forms.CharField(widget=forms.HiddenInput())


from django import forms
from .models import AllocatedMechanic, CustomUser, Slot

class MechanicAllocationForm(forms.Form):
    mechanic = forms.ModelChoiceField(
        queryset=Mechanic.objects.filter(level=MechanicLevel.SENIOR, status=MechanicStatus.ACTIVE),
        label="Select Senior Mechanic",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
   
  

# class MechanicAllocationForm(forms.ModelForm):
#     class Meta:
#         model = AllocatedMechanic
#         fields = ['mechanic', 'slot']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['mechanic'].queryset = Mechanic.objects.filter(level=MechanicLevel.SENIOR, status=MechanicStatus.ACTIVE)


# class MechanicAllocationForm(forms.ModelForm):
#     mechanic = forms.ModelChoiceField(
#         queryset=CustomUser.objects.filter(role=UserRole.MECHANIC),
#         label="Select Mechanic"
#     )
#     slot = forms.ModelChoiceField(
#         queryset=Slot.objects.all(),
#         label="Select Slot"
#     )

#     class Meta:
#         model = AllocatedMechanic
#         fields = ['mechanic', 'slot']


#/////////////////////   Change Password form ?//////////////

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = get_user_model()
        fields = ['old_password', 'new_password1', 'new_password2']


#///////////////    Add Vehicle in Customer Page /////////////////////

# from django import forms
# from .models import Vehicle

# class AddVehicleForm(forms.ModelForm):
#     class Meta:
#         model = Vehicle
#         fields = ['vehicle_model', 'registration_number']
#         widgets = {
#             'vehicle_model': forms.Select(attrs={'class': 'form-control'}),
#             'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
#         }


from django import forms
from .models import Vehicle

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['registration_number']  # Only the registration number will be filled by the user
        widgets = {
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter vehicle registration number',
                'required': True
            }),
        }
        labels = {
            'registration_number': 'Vehicle Registration Number'
        }


#/////////////////   Add service category in admin page /////////////////////

from django import forms
from .models import ServiceCategory

class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'image', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }




class ServiceTypeForm(forms.ModelForm):
    class Meta:
        model = ServiceType
        fields = ['name', 'image', 'description', 'service_time']


class ServicePriceForm(forms.ModelForm):
    class Meta:
        model = ServicePrice
        fields = ['price']

# forms.py
from django import forms
from .models import CustomerComplaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = CustomerComplaint
        fields = ['complaint']
        widgets = {
            'complaint': forms.Textarea(attrs={'placeholder': 'Enter your complaint here...'}),
        }


#////////////  job Portal //////////////////

# forms.py
from django import forms
from .models import JobPost, JobApplication

# class JobPostForm(forms.ModelForm):
#     class Meta:
#         model = JobPost
#         fields = ['title', 'description', 'company_name']

class JobPostForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter job title',
        }),
        help_text='Enter a clear and concise job title'
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter detailed job description',
            'rows': 5
        }),
        help_text='Provide comprehensive details about the role, responsibilities, and requirements'
    )
    
    company_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter company name',
        }),
        help_text='Enter the name of your company'
    )

    class Meta:
        model = JobPost
        fields = ['title', 'description', 'company_name']


# class JobApplicationForm(forms.ModelForm):
#     class Meta:
#         model = JobApplication
#         fields = ['candidate_name', 'candidate_email', 'resume']

from django import forms
from django.core.validators import FileExtensionValidator

class JobApplicationForm(forms.ModelForm):
    candidate_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )
    
    candidate_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    resume = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx'
        })
    )

    class Meta:
        model = JobApplication
        fields = ['candidate_name', 'candidate_email', 'resume']
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if resume.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('File size must be no more than 5MB')
        return resume