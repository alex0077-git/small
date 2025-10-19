from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .form import CustomUserCreationForm, UserDetailsForm
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .models import *
from .form import *
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    user = request.user
    return render(request,'index.html',{'user' : user})
def about(request) :
    return render(request,"about.html")
def contact(request) :
    return render(request,"contact.html")

#//////////////////////////CUSTOMER LOGIN  /////////////////////////////
def cust_login(request) :
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'Successfully logged in.')
                if user.role == 'admin':
                    return redirect('cst_admin')
                elif user.role == 'service_manager':
                    return redirect('manager_dashboard')
                elif user.role == 'mechanic':
                     return redirect('mechanic_dashboard')
                elif user.role == 'customer':
                     return redirect('home')


                  # Replace 'home' with your desired redirect URL
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = AuthenticationForm()
    return render(request,"cust_login.html",{'form': form})



#////////////////  Password Reset /////////////////////////////
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import CustomUser

class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password/password_reset.html'
    email_template_name = 'password/password_reset_email.html'
    subject_template_name = 'password/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    success_message = "An email has been sent with instructions to reset your password"
    
    def form_valid(self, form):
        # """
        # Validates the form and checks if the email exists in the database
        # """
        email = form.cleaned_data['email']
        if not CustomUser.objects.filter(email=email).exists():
            messages.error(self.request, "This email address is not registered with us.")
            return self.form_invalid(form)
        return super().form_valid(form)
    

    #///////////////////  Change Password ///////////////////////


def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()  # Saves the new password
            update_session_auth_hash(request, user)  # Keeps the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')  # Redirect to the profile page or desired page
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})


#//////////////////////////  Registration Views ///////////////////////////////////////

def cust_register(request) :
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        details_form = UserDetailsForm(request.POST)
        if user_form.is_valid() and details_form.is_valid():
            user = user_form.save()
            details = details_form.save(commit=False)
            details.user = user
            details.save()
            messages.success(request, 'Registered Successfully.')
            login(request, user)
            return redirect('customerLogin')  
    else:
        user_form = CustomUserCreationForm()
        details_form = UserDetailsForm()
    return render(request,"cust_register.html",{'user_form': user_form, 'details_form': details_form})


#///////////////////////////   ADD VEHICLES   /////////////////////////////////////////////

def select_vehicle(request):
    user = request.user
    vehicles = Vehicle.objects.filter(user=user)

    if request.method == 'POST':
        selected_vehicle_id = request.POST.get('selected_vehicle')
        if selected_vehicle_id:
            selected_vehicle = get_object_or_404(Vehicle, id=selected_vehicle_id, user=user)
            # You can now do something with the selected vehicle, like setting it as the current vehicle in the session
            request.session['selected_vehicle_id'] = selected_vehicle.id
            request.session['selected']=1
            return redirect('home')  # Redirect to wherever you need after selection

    return render(request, 'vehicle/select_vehicle.html', {'vehicles': vehicles})


def vehicle_brand(request):
    vehicle_makes = VehicleMake.objects.all()  # Fetch all vehicle makes (brands)
    return render(request, 'vehicle/vehicle_brand.html', {'vehicle_makes': vehicle_makes})
    

# View to display variants for a selected brand
def vehicle_variants(request, brand_id):
    brand = get_object_or_404(VehicleMake, id=brand_id)  # Fetch the selected brand by ID
    variants = VehicleModel.objects.filter(make=brand)  # Fetch all variants related to the selected brand
    return render(request, 'vehicle/vehicle_variants.html', {'brand': brand, 'variants': variants})


def add_vehicle_number(request, variant_id):
    vehicle_variant = get_object_or_404(VehicleModel, id=variant_id)
    
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            registration_number = form.cleaned_data['registration_number']
            
            # Check if the registration number already exists
            if Vehicle.objects.filter(registration_number=registration_number).exists():
                error_message = "This registration number is already registered."
                return render(request, 'vehicle/add_vehicle_number.html', {
                    'vehicle_variant': vehicle_variant,
                    'form': form,
                    'error_message': error_message
                })

            # Create and save the new vehicle
            vehicle = Vehicle.objects.create(
                user=request.user,
                vehicle_model=vehicle_variant,
                registration_number=registration_number
            )
            vehicle.save()

            # Redirect to some success page or homepage
            return redirect('home')  # Or wherever you want to redirect
    
    else:
        form = VehicleForm()

    return render(request, 'vehicle/add_vehicle_number.html', {
        'vehicle_variant': vehicle_variant,
        'form': form
    })

#//////////////  Services For Customer //////////////////////////////

def customer_service_category(request):
    service_categories = ServiceCategory.objects.all()
    return render(request, 'service/cst_service_category.html', {'service_categories': service_categories})

# View for listing service types of a selected category
from django.shortcuts import render, get_object_or_404
from .models import ServiceCategory, ServiceType, ServicePrice, Vehicle, VehicleModel

# def customer_service_type(request, category_id):
#     # Get the selected vehicle from the session
#     selected_vehicle_id = request.session.get('selected_vehicle_id')

#     # Ensure the vehicle is selected
#     if not selected_vehicle_id:
#         return redirect('select_vehicle')  # Redirect to vehicle selection if not selected

#     # Get the selected vehicle model
#     selected_vehicle = get_object_or_404(Vehicle, id=selected_vehicle_id)
#     vehicle_variant = selected_vehicle.vehicle_model

#     # Get the service category and service types for this category
#     service_category = get_object_or_404(ServiceCategory, id=category_id)
#     service_types = ServiceType.objects.filter(category=service_category)

#     # Fetch service prices for each service type for the selected vehicle variant
#     service_type_prices = []
#     for service_type in service_types:
#         service_price = ServicePrice.objects.filter(service_type=service_type, vehicle_model=vehicle_variant).first()
#         service_type_prices.append({
#             'service_type': service_type,
#             'price': service_price.price if service_price else 'Price not available',
#             'description': service_price.description if service_price else ''
#         })

#     return render(request, 'service/cst_service_type.html', {
#         'service_category': service_category,
#         'service_type_prices': service_type_prices,
#         'vehicle_variant': vehicle_variant
#     })

@login_required(login_url='customerLogin')
def customer_service_type(request, category_id):
    # Get the selected vehicle from the session
    selected_vehicle_id = request.session.get('selected_vehicle_id')

    # Ensure the vehicle is selected
    if not selected_vehicle_id:
        return redirect('select_vehicle')  # Redirect to vehicle selection if not selected

    # Get the selected vehicle model
    selected_vehicle = get_object_or_404(Vehicle, id=selected_vehicle_id)
    vehicle_variant = selected_vehicle.vehicle_model

    # Get the service category and service types for this category
    service_category = get_object_or_404(ServiceCategory, id=category_id)
    service_types = ServiceType.objects.filter(category=service_category)

    # Fetch service prices for each service type for the selected vehicle variant
    service_type_prices = []
    for service_type in service_types:
        service_price = ServicePrice.objects.filter(service_type=service_type, vehicle_model=vehicle_variant).first()
        
        # Check if the service type is already in the user's cart for this vehicle
        is_in_cart = ServiceCart.objects.filter(
            user=request.user, service_type=service_type, vehicle=selected_vehicle
        ).exists()
        
        service_type_prices.append({
            'service_type': service_type,
            'price': service_price.price if service_price else 'Price not available',
            'description': service_price.description if service_price else '',
            'is_in_cart': is_in_cart  # Pass the cart status
        })

    return render(request, 'service/cst_service_type.html', {
        'service_category': service_category,
        'service_type_prices': service_type_prices,
        'vehicle_variant': vehicle_variant
    })




#////////////////////////////// Service Cart ////////////////////////

from django.http import JsonResponse
from .models import ServiceCart

# def add_to_cart(request):
#     if request.method == 'POST':
#         service_type_id = request.POST.get('service_type_id')
#         vehicle_id = request.session.get('selected_vehicle_id')

#         service_type = ServiceType.objects.get(id=service_type_id)
#         vehicle = Vehicle.objects.get(id=vehicle_id)

#         # Check if item already in cart
#         cart_item, created = ServiceCart.objects.get_or_create(
#             user=request.user,
#             service_type=service_type,
#             vehicle=vehicle
#         )

#         if not created:
#             return JsonResponse({'message': 'Item already in cart'}, status=400)

#         return JsonResponse({'message': 'Added to cart successfully'}, status=200)

# def view_cart(request):
#     vehicle_id = request.session.get('selected_vehicle_id')
#     vehicle = Vehicle.objects.get(id=vehicle_id)

#     cart_items = ServiceCart.objects.filter(user=request.user, vehicle=vehicle)

#     return render(request, 'service/view_cart.html', {
#         'cart_items': cart_items,
#         'vehicle': vehicle
#     })

# def remove_from_cart(request, cart_item_id):
#     cart_item = get_object_or_404(ServiceCart, id=cart_item_id)
#     cart_item.delete()
#     return JsonResponse({'message': 'Removed from cart'}, status=200)

# def add_to_cart(request):
#     if request.method == 'POST':
#         service_type_id = request.POST.get('service_type_id')
#         vehicle_id = request.session.get('selected_vehicle_id')

#         # Ensure that service type and vehicle are valid
#         service_type = get_object_or_404(ServiceType, id=service_type_id)
#         vehicle = get_object_or_404(Vehicle, id=vehicle_id)

#         # Add service to cart
#         ServiceCart.objects.create(service_type=service_type, vehicle=vehicle)

#         return JsonResponse({'message': 'Added to cart successfully'})

#     return JsonResponse({'message': 'Failed to add to cart'}, status=400)
from django.contrib.auth.decorators import login_required

# @login_required
# def add_to_cart(request, service_type_id):
#     # Get the logged-in user
#     user = request.user

#     # Get the service type and selected vehicle
#     service_type = get_object_or_404(ServiceType, id=service_type_id)
#     selected_vehicle_id = request.session.get('selected_vehicle_id')

#     # Ensure the vehicle is selected
#     if not selected_vehicle_id:
#         return redirect('select_vehicle')  # Redirect to vehicle selection if not selected

#     vehicle = get_object_or_404(Vehicle, id=selected_vehicle_id)

#     # Create or update the service cart
#     ServiceCart.objects.create(user=user, service_type=service_type, vehicle=vehicle)

#     return redirect('customer_service_type', category_id=service_type.category.id)
from django.contrib.auth.decorators import login_required
# @login_required
# def add_to_cart(request, service_type_id):
#     if request.method == 'POST':
#         user = request.user
#         service_type = get_object_or_404(ServiceType, id=service_type_id)
#         selected_vehicle_id = request.session.get('selected_vehicle_id')

#         if not selected_vehicle_id:
#             return redirect('select_vehicle')  # Redirect to vehicle selection if not selected

#         vehicle = get_object_or_404(Vehicle, id=selected_vehicle_id)

#         # Create or update the service cart
#         ServiceCart.objects.create(user=user, service_type=service_type, vehicle=vehicle)

#         return JsonResponse({'message': 'Added to cart successfully'})
#     return JsonResponse({'message': 'Invalid request'}, status=400)

@login_required
def add_to_cart(request, service_type_id):
    if request.method == 'POST':
        user = request.user
        service_type = get_object_or_404(ServiceType, id=service_type_id)
        selected_vehicle_id = request.session.get('selected_vehicle_id')

        if not selected_vehicle_id:
            return redirect('select_vehicle')  # Redirect to vehicle selection if not selected

        vehicle = get_object_or_404(Vehicle, id=selected_vehicle_id)

        # Create a new ServiceCart entry
        cart_item = ServiceCart.objects.create(user=user, service_type=service_type, vehicle=vehicle)

        return JsonResponse({'message': 'Added to cart successfully', 'cart_item_id': cart_item.id})
    return JsonResponse({'message': 'Invalid request'}, status=400)



# View Cart
# def view_cart(request):
#     vehicle_id = request.session.get('selected_vehicle_id')
#     vehicle = get_object_or_404(Vehicle, id=vehicle_id)
#     cart_items = ServiceCart.objects.filter(vehicle=vehicle)

#     return render(request, 'service/view_cart.html', {
#         'vehicle': vehicle,
#         'cart_items': cart_items,
#     })


@login_required(login_url='customerLogin')
def view_cart(request):
    if not request.session.get('selected'):
        return redirect('select_vehicle')
    vehicle_id = request.session.get('selected_vehicle_id')
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    cart_items = ServiceCart.objects.filter(vehicle=vehicle)

    # Calculate total price and total service time
    total_price = sum(item.service_type.service_prices.first().price for item in cart_items)
    total_time = sum(item.service_type.service_time for item in cart_items)

    # Convert time to hours and minutes
    
    return render(request, 'service/view_cart.html', {
        'vehicle': vehicle,
        'cart_items': cart_items,
        'total_price': total_price,
        'total_time': total_time,
        
    })




# Remove from Cart
from django.http import JsonResponse



@login_required
def remove_from_cart(request, cart_item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(ServiceCart, id=cart_item_id)
        service_type_id = cart_item.service_type.id
        cart_item.delete()
        return JsonResponse({'message': 'Removed from cart', 'service_type_id': service_type_id})
    return JsonResponse({'message': 'Invalid request'}, status=400)


#////////////////   Order Items //////////////////////////////////
import uuid
from django.shortcuts import get_object_or_404, redirect
from .models import Order, OrderService, ServiceCart


# def order_confirmation(request):
#     user = request.user
#     cart_items = ServiceCart.objects.filter(user=user)

#     if cart_items.exists():
#         vehicle = cart_items.first().vehicle  # Assuming all cart items are for the same vehicle

#         # Render the order confirmation page with cart details (no order_id yet)
#         return render(request, 'service/order_confirmation.html', {
#             'cart_items': cart_items,
#             'vehicle': vehicle,
#         })
#     else:
#         return redirect('view_cart')  # If no cart items, redirect back to the cart

def order_confirmation(request):
    user = request.user
    cart_items = ServiceCart.objects.filter(user=user)

    if cart_items.exists():
        vehicle = cart_items.first().vehicle  # Assuming all cart items are for the same vehicle

        # Get the user details
        user_details = UserDetails.objects.get(user=user)
        # Calculate total price and total service time
        total_price = sum(item.service_type.service_prices.first().price for item in cart_items)
        total_time = sum(item.service_type.service_time for item in cart_items)

        # Convert time to hours and minutes if necessary (optional)

        # Render the order confirmation page with cart details
        return render(request, 'service/order_confirmation.html', {
            'cart_items': cart_items,
            'vehicle': vehicle,
            'total_price': total_price,
            'total_time': total_time,
            'user_details': user_details,
        })
    else:
        return redirect('view_cart')  # If no cart items, redirect back to the cart




from django.http import JsonResponse
import uuid  # For generating unique order ID

# def create_order(request):
#     if request.method == 'POST':
#         user = request.user
#         # No need for `order_id` from frontend, it will be generated here
#         cart_items = ServiceCart.objects.filter(user=user)

#         if cart_items.exists():
#             vehicle = cart_items.first().vehicle  # Assuming all cart items are for the same vehicle
            
#             # Generate unique order ID
#             order_id = str(uuid.uuid4()).replace('-', '').upper()[:12]

#             # Create the order
#             order = Order.objects.create(user=user, vehicle=vehicle, order_id=order_id)

#             # Add the services to the order
#             for item in cart_items:
#                 OrderService.objects.create(order=order, service_type=item.service_type, price=item.service_type.service_prices.first().price)

#             # Clear the cart after creating the order
#             cart_items.delete()

#             return JsonResponse({'success': True, 'order_id': order_id})  # Send back the order ID
#         else:
#             return JsonResponse({'success': False, 'message': 'Cart is empty'})
    
#     return JsonResponse({'success': False, 'message': 'Invalid request method'})

# from django.http import JsonResponse
# import uuid, json
# from django.utils.dateparse import parse_date

# def create_order(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         service_date = parse_date(data.get('service_date'))  # Get the selected service date

#         user = request.user
#         cart_items = ServiceCart.objects.filter(user=user)

#         if cart_items.exists():
#             vehicle = cart_items.first().vehicle
#             order_id = str(uuid.uuid4()).replace('-', '').upper()[:12]

#             # Create the order with the selected service date
#             order = Order.objects.create(user=user, vehicle=vehicle, order_id=order_id, service_date=service_date)

#             # Add services to the order
#             for item in cart_items:
#                 OrderService.objects.create(order=order, service_type=item.service_type, price=item.service_type.service_prices.first().price)

#             # Clear the cart after creating the order
#             cart_items.delete()

#             return JsonResponse({'success': True, 'order_id': order_id})
#         else:
#             return JsonResponse({'success': False, 'message': 'Cart is empty'})
    
#     return JsonResponse({'success': False, 'message': 'Invalid request method'})


from django.http import JsonResponse
import uuid, json
from django.utils.dateparse import parse_date

def create_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        service_date = parse_date(data.get('service_date'))  # Get the selected service date

        user = request.user
        cart_items = ServiceCart.objects.filter(user=user)

        if cart_items.exists():
            vehicle = cart_items.first().vehicle
            order_id = str(uuid.uuid4()).replace('-',   '').upper()[:12]

            try:
                # Create the order with the selected service date
                order = Order.objects.create(user=user, vehicle=vehicle, order_id=order_id, service_date=service_date)

                # Add services to the order
                for item in cart_items:
                    OrderService.objects.create(order=order, service_type=item.service_type, price=item.service_type.service_prices.first().price)

                # Clear the cart after creating the order
                cart_items.delete()

                return JsonResponse({'success': True, 'order_id': order_id})

            except ValueError as e:
                # Handle the case where no free slots are available
                return JsonResponse({'success': False, 'message': str(e)})

        else:
            return JsonResponse({'success': False, 'message': 'Cart is empty'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})



from django.shortcuts import render
from .models import Order, Vehicle
from django.db.models import Sum

from django.db.models import Sum
from django.shortcuts import render
from .models import Order, Vehicle

from django.db.models import Sum
from django.shortcuts import render
from .models import Order, Vehicle

@login_required(login_url='customerLogin')
def my_orders(request):
    # Get the current logged-in user
    user = request.user

    # Fetch all vehicles owned by the user
    vehicles = Vehicle.objects.filter(user=user)

    # Check if a specific vehicle is selected for filtering
    selected_vehicle_id = request.GET.get('vehicle_id')

    # Initialize orders as an empty queryset just in case
    orders = Order.objects.none()

    # Filter orders by user and optionally by selected vehicle
    if selected_vehicle_id:
        orders = Order.objects.filter(user=user, vehicle_id=selected_vehicle_id).order_by('-order_date')
    else:
        orders = Order.objects.filter(user=user).order_by('-order_date')

    # Annotate each order with the total price
    for order in orders:
        total_price = order.services.aggregate(total=Sum('price'))['total'] or 0.00
        order.total_price = total_price

    context = {
        'orders': orders,
        'vehicles': vehicles,
        'selected_vehicle_id': selected_vehicle_id,  # Pass the selected vehicle ID to the template
    }

    return render(request, 'my_order.html', context)







def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out.')
    return redirect('home')

def price(request) :
    return render(request,"price.html")
def service(request) :
    return render(request,"service.html")
def booking(request) :
    return render(request,"booking.html")
def location(request) :
    return render(request,"location.html")


@login_required
def cst_admin(request):
    # Retrieve all orders
    orders = Order.objects.select_related('user', 'vehicle', 'allocated_slot').prefetch_related('services').all()
    slots = Slot.objects.all()
    return render(request, 'admin/dashboard.html', {'orders': orders, 'slots': slots})


from django.shortcuts import render
from .models import Order, OrderService

# @login_required
# def all_orders(request):
#     # Retrieve all orders
#     orders = Order.objects.select_related('user', 'vehicle', 'allocated_slot').prefetch_related('services').all()

#     return render(request, 'admin/dashboard.html', {'orders': orders})


from django.shortcuts import render, redirect
from .form import VehicleMakeForm, VehicleModelForm

def create_vehicle_make(request):
    if request.method == 'POST':
        form = VehicleMakeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('vehicle_make_success')  # Redirect to a success page or list view
    else:
        form = VehicleMakeForm()

    return render(request, 'admin/vehicle_make_form.html', {'form': form})

def create_vehicle_model(request):
    if request.method == 'POST':
        form = VehicleModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('vehicle_model_success')  # Redirect to a success page or list view
    else:
        form = VehicleModelForm()

    return render(request, 'admin/add_vehicle_model.html', {'form': form})

def manage_vehicle(request) :
    vehicle_makes = VehicleMake.objects.all()
    return render(request, 'admin/manage_vehicle.html',{'vehicle_makes': vehicle_makes})


#//////////////// Slot List ????????????????????????????????????????????

# def Slotlist(request):
#     slots = Slot.objects.all() 
#     return render(request, 'admin/slot_list.html',  {'form': forms, 'slot': slots})

def manageSlot (request):
    if request.method == 'POST':
        form = SlotForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new slot to the database
            return redirect('slot_list')  # Redirect to the list of slots or a success page
    else:
        form = SlotForm()
    return render (request,"admin/addslot.html",{'form':form})

def slot_list(request):
    slots = Slot.objects.all()
    form = ManagerAllocationForm()

    context = {
        'slots': slots,
        'form': form
    }
    return render(request, 'admin/slot_list.html', context)


# def allocate_manager(request, slug):
#     slot = get_object_or_404(Slot, slug=slug)

#     if request.method == 'POST':
#         form = AllocateManagerForm(request.POST)
#         if form.is_valid():
#             # Create or update the allocated manager
#             AllocatedManager.objects.update_or_create(
#                 slot=slot,
#                 defaults={'manager': form.cleaned_data['manager']}
#             )
#             slot.status = SlotStatus.ALLOCATED  # Update the slot status
#             slot.save()
#             return redirect('slot_list')  # Redirect to the slot list
#     else:
#         form = AllocateManagerForm()  # Create a new form instance

#     return render(request, 'admin/addslot.html', {'form': form, 'slot': slot})

def allocate_manager(request, slug):
    slot = get_object_or_404(Slot, slug=slug)
    if request.method == 'POST':
        form = ManagerAllocationForm(request.POST)
        if form.is_valid():
            manager = form.cleaned_data.get('manager')
            AllocatedManager.objects.update_or_create(
                slot=slot,
                defaults={'manager': manager}
            )
            return redirect('slot_list')
    return redirect('slot_list')



#/////////////// add vehicle by admin ////////////////////

def add_vehicle_model(request, brand_id):
    brand = get_object_or_404(VehicleMake, id=brand_id)

    if request.method == 'POST':
        form = VehicleModelForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle_model = form.save(commit=False)
            vehicle_model.make = brand  # Link the vehicle model to the selected brand
            vehicle_model.save()
            return redirect('brand_variants', brand_id=brand.id)  # Redirect to the brand variants page
    else:
        form = VehicleModelForm()

    return render(request, 'admin/add_vehicle_model.html', {'form': form, 'brand': brand})


def brand_variants(request, brand_id):
    brand = get_object_or_404(VehicleMake, id=brand_id)
    variants = VehicleModel.objects.filter(make=brand)
    return render(request, 'admin/brand_variants.html', {'brand': brand, 'variants': variants})


#////////////////////////// CUSTOMER PROFILE ////////////////////////
from django.contrib.auth.decorators import login_required

@login_required
def customer_profile(request):
    user_details = get_object_or_404(UserDetails, user=request.user)
    return render(request, 'customer_profile.html', {'user_details': user_details})

@login_required
def edit_profile(request):
    user_details = get_object_or_404(UserDetails, user=request.user)

    if request.method == 'POST':
        form = UserDetailsForm(request.POST, instance=user_details)
        if form.is_valid():
            form.save()
            return redirect('customer_profile')
    else:
        form = UserDetailsForm(instance=user_details)
    
    return render(request, 'edit_profile.html', {'form': form})





#/////////////////Service Manager Dashboard/////////////////////////

# @login_required
# def manager_dashboard(request):
#     # Get the logged-in service manager
#     manager = request.user

#     # Retrieve the slots assigned to the service manager
#     assigned_slots = AllocatedManager.objects.filter(manager=manager)

#     # Initialize the mechanic variable
#     mechanic = CustomUser.objects.filter(role ='mechanic')
#     print(mechanic)

#     if request.method == 'POST':
#         form = AssignMechanicForm(request.POST)
#         if form.is_valid():
#             slot_id = form.cleaned_data['slot_id']
#             mechanic = form.cleaned_data['mechanic']

#             # Assign the mechanic to the selected slot
#             slot = Slot.objects.get(id=slot_id)
#             slot.mechanic = mechanic
#             slot.save()

#             return redirect('manager_dashboard')  # Refresh the dashboard after assigning the mechanic
#     else:
#         form = AssignMechanicForm()

#     return render(
#         request, 
#         'serviceManager/dashboard.html', 
#         {
#             'assigned_slots': assigned_slots,
#             'mechanics': mechanic,  # mechanic will be None in GET requests
#             'form': form,
#             'user': request.user
#         }
#     )



# @login_required
# def manager_dashboard(request):
#     # Get the logged-in service manager
#     manager = request.user

#     # Retrieve the slots assigned to the service manager
#     assigned_slots = AllocatedManager.objects.filter(manager=manager)

#     # Filter only senior mechanics who are not "working"
#     mechanics = Mechanic.objects.filter(level=MechanicLevel.SENIOR, status=MechanicStatus.ACTIVE)

#     if request.method == 'POST':
#         form = AssignMechanicForm(request.POST)
#         if form.is_valid():
#             slot_id = form.cleaned_data['slot_id']
#             mechanic = form.cleaned_data['mechanic']

#             # Assign the mechanic to the selected slot
#             slot = Slot.objects.get(id=slot_id)
#             slot.mechanic = mechanic.user
#             slot.save()

#             # Update mechanic's status to working
#             mechanic.status = MechanicStatus.WORKING
#             mechanic.save()

#             return redirect('manager_dashboard')  # Refresh the dashboard after assigning the mechanic
#     else:
#         form = AssignMechanicForm()

#     return render(
#         request, 
#         'serviceManager/dashboard.html', 
#         {
#             'assigned_slots': assigned_slots,
#             'mechanics': mechanics,  # Senior mechanics who are available
#             'form': form,
#             'user': request.user
#         }
#     )

@login_required
def manager_dashboard(request):
    # Get the logged-in service manager
    manager = request.user

    # Retrieve the slots assigned to the service manager
    assigned_slots = AllocatedManager.objects.filter(manager=manager)

    # Get a list of slot IDs assigned to the manager
    assigned_slot_ids = assigned_slots.values_list('slot_id', flat=True)

    # Retrieve orders that are allocated to these slots
    orders = Order.objects.filter(allocated_slot__in=assigned_slot_ids)

    # Filter only senior mechanics who are not "working"
    mechanics = Mechanic.objects.filter(level=MechanicLevel.SENIOR, status=MechanicStatus.ACTIVE)

    # Fetch all slots allocated to the logged-in service manager
    slots_with_allocated_mechanics = Slot.objects.filter(id__in=assigned_slot_ids).prefetch_related('allocatedmechanic_set')

    return render(
        request, 
        'serviceManager/dashboard.html', 
        {
            'assigned_slots': assigned_slots,
            'slots_with_allocated_mechanics': slots_with_allocated_mechanics,  # Slots with their allocated mechanics
            'mechanics': mechanics,  # Senior mechanics who are available
            'orders': orders,  # Orders related to the slots
            'user': request.user
        }
    )

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from .models import Slot, AllocatedMechanic, Mechanic, MechanicStatus, MechanicLevel
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from autocareweb.models import Slot, Mechanic, AllocatedMechanic, MechanicStatus
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction

def allocate_mechanic(request, slot_slug):
    slot = get_object_or_404(Slot, slug=slot_slug)

    # Filter available senior mechanics
    available_mechanics = Mechanic.objects.filter(level=MechanicLevel.SENIOR, status=MechanicStatus.ACTIVE)

    if request.method == "POST":
        form = MechanicAllocationForm(request.POST)

        if form.is_valid():
            mechanic = form.cleaned_data['mechanic']

            try:
                with transaction.atomic():
                    # Assign the mechanic to the slot
                    slot.mechanic = mechanic.mechanic  # Assign the CustomUser instance from the Mechanic object
                    slot.save()

                    # Update mechanic status to working
                    mechanic.status = MechanicStatus.WORKING
                    mechanic.save()

                    # Add record to AllocatedMechanic table
                    AllocatedMechanic.objects.create(mechanic=mechanic.mechanic, manager=request.user, slot=slot)

                return redirect('manager_dashboard')
            except Exception as e:
                # Handle any database errors
                print("Error in allocation: ", e)
                return redirect('manager_dashboard')
        else:
            print("Form errors: ", form.errors)

    return JsonResponse({'error': 'Invalid form submission'}, status=400)






from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Slot, AllocatedMechanic, Mechanic, MechanicStatus

@require_POST
@login_required
def remove_mechanic(request):
    slot_id = request.POST.get('slot_id')
    
    # Ensure slot_id is provided
    if not slot_id:
        return JsonResponse({'error': 'No slot ID provided'}, status=400)
    
    # Fetch the slot
    slot = get_object_or_404(Slot, id=slot_id)
    
    # Check if the slot already has no mechanic assigned
    if not slot.mechanic:
        return JsonResponse({'error': 'No mechanic is currently assigned to this slot'}, status=400)
    
    try:
        # Fetch the allocated mechanic associated with this slot
        allocated_mechanic = AllocatedMechanic.objects.get(slot=slot)
    except AllocatedMechanic.DoesNotExist:
        return JsonResponse({'error': 'No mechanic allocation found for this slot'}, status=400)

    try:
        # Atomic transaction to ensure consistent data
        with transaction.atomic():
            # Remove mechanic from slot
            slot.mechanic = None
            slot.save()

            # Set the mechanic status back to ACTIVE
            mechanic = Mechanic.objects.get(mechanic=allocated_mechanic.mechanic)
            mechanic.status = MechanicStatus.ACTIVE
            mechanic.save()

            # Delete the allocation record from AllocatedMechanic
            allocated_mechanic.delete()

        return JsonResponse({'message': 'Mechanic removed successfully!'})

    except Mechanic.DoesNotExist:
        return JsonResponse({'error': 'Mechanic not found'}, status=400)

    except Exception as e:
        # Handle general exceptions and log them
        print("Error removing mechanic: ", e)
        return JsonResponse({'error': 'An error occurred while removing the mechanic'}, status=500)




#/////////////////Mechanic Dashboard/////////////////////////



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Slot, Mechanic, AllocateJuniorMechanics, MechanicStatus, MechanicLevel
from django.http import JsonResponse

# @login_required
# def mechanic_dashboard(request):
#     mechanic = get_object_or_404(Mechanic, mechanic=request.user)

#     if mechanic.level == MechanicLevel.SENIOR:
#         # Get slots assigned to the senior mechanic
#         senior_slots = Slot.objects.filter(allocatedmechanic__mechanic=request.user)
#         available_junior_mechanics = Mechanic.objects.filter(
#             level__in=[MechanicLevel.MEDIUM, MechanicLevel.ENTRY], 
#             status=MechanicStatus.ACTIVE
#         ).exclude(
#             allocatedjuniormechanics__slot__in=senior_slots
#         )

#         return render(request, 'mechanics/mechanic_dashboard.html', {
#             'mechanic': mechanic,
#             'senior_slots': senior_slots,
#             'available_junior_mechanics': available_junior_mechanics
#         })

#     else:
#         # Get slots assigned to the junior or entry-level mechanic
#         junior_slots = AllocateJuniorMechanics.objects.filter(junior_mechanic=request.user)

#         return render(request, 'mechanic_dashboard.html', {
#             'mechanic': mechanic,
#             'junior_slots': junior_slots



# @login_required
# def mechanic_dashboard(request):
#     user = request.user

#     # Fetch senior mechanics
#     if user.mechanic.level == MechanicLevel.SENIOR:
#         # Fetch slots allocated to the senior mechanic using the CustomUser instance
#         # assigned_slots = AllocatedMechanic.objects.filter(mechanic=user)
#         assigned_slots = Slot.objects.filter(mechanic=request.user)
#         # Fetch medium and entry mechanics that have not been allocated to any slot by this senior mechanic
#         available_junior_mechanics = Mechanic.objects.filter(
#             level__in=[MechanicLevel.MEDIUM, MechanicLevel.ENTRY],
#             status=MechanicStatus.ACTIVE
#         )

#         context = {
#             'assigned_slots': assigned_slots,
#             'available_junior_mechanics': available_junior_mechanics,
#         }

#     else:
#         # For medium/entry mechanics, show the slots they've been allocated to
#         assigned_slots = AllocateJuniorMechanics.objects.filter(junior_mechanic=user)

#         context = {
#             'assigned_slots': assigned_slots,
#         }

#     return render(request, 'mechanics/mechanic_dashboard.html', context)



# @login_required
# def add_junior_mechanic(request, slot_id):
#     slot = get_object_or_404(Slot, id=slot_id)
#     senior_mechanic = get_object_or_404(Mechanic, mechanic=request.user, level=MechanicLevel.SENIOR)

#     if request.method == 'POST':
#         junior_mechanic_id = request.POST.get('junior_mechanic')
#         junior_mechanic = get_object_or_404(Mechanic, id=junior_mechanic_id, status=MechanicStatus.ACTIVE)

#         # Allocate junior mechanic
#         AllocateJuniorMechanics.objects.create(
#             junior_mechanic=junior_mechanic.mechanic,
#             senior_mechanic=request.user,
#             slot=slot
#         )

#         # Mark the junior mechanic as working
#         junior_mechanic.status = MechanicStatus.WORKING
#         junior_mechanic.save()

#         return redirect('mechanic')

# @login_required
# def remove_junior_mechanic(request, slot_id, junior_mechanic_id):
#     slot = get_object_or_404(Slot, id=slot_id)
#     junior_mechanic = get_object_or_404(Mechanic, mechanic__id=junior_mechanic_id)

#     # Remove the junior mechanic from the slot
#     allocation = get_object_or_404(AllocateJuniorMechanics, slot=slot, junior_mechanic=junior_mechanic.mechanic)
#     allocation.delete()

#     # Update mechanic status back to active
#     junior_mechanic.status = MechanicStatus.ACTIVE
#     junior_mechanic.save()

#     return redirect('mechanic')




@login_required
def mechanic_dashboard(request):
    user = request.user

    if user.mechanic.level == MechanicLevel.SENIOR:
        assigned_slots = Slot.objects.filter(mechanic=user)
        orders = Order.objects.filter(allocated_slot__in=assigned_slots).prefetch_related('services', 'vehicle', 'user')
        available_junior_mechanics = Mechanic.objects.filter(
            level__in=[MechanicLevel.MEDIUM, MechanicLevel.ENTRY],
            status=MechanicStatus.ACTIVE
        )
        context = {
            'assigned_slots': assigned_slots,
            'available_junior_mechanics': available_junior_mechanics,
            'orders': orders, 
        }
    else:
        assigned_slots = AllocateJuniorMechanics.objects.filter(junior_mechanic=user)
        context = {'assigned_slots': assigned_slots,
                   'orders': orders, 
        }

    return render(request, 'mechanics/mechanic_dashboard.html', context)




def update_order_status(request):
    # Fetch all orders that belong to the logged-in senior mechanic
    assigned_orders = Order.objects.filter(allocated_slot__mechanic=request.user)

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')

        # Fetch the order object by ID
        order = get_object_or_404(Order, id=order_id)

        # Update the order status
        order.status = new_status
        order.save()

        # If the status is 'completed', free up the slot
        if new_status == 'completed':
            slot = order.allocated_slot
            slot.status = SlotStatus.FREE
            slot.save()

        # Send a success message
        messages.success(request, "Order status updated successfully!")

        # Return a success response
        return JsonResponse({'success': True})

    return render(request, 'mechanics/update_order.html', {'orders': assigned_orders})


@login_required
def allocate_juniormechanic(request):
    # Fetch all slots and available junior mechanics for senior mechanics
    available_junior_mechanics = Mechanic.objects.filter(
        level__in=[MechanicLevel.MEDIUM, MechanicLevel.ENTRY],
        status=MechanicStatus.ACTIVE
    )
    slots = Slot.objects.filter(mechanic=request.user)

    context = {
        'slots': slots,
        'available_junior_mechanics': available_junior_mechanics
    }
    return render(request, 'mechanics/allocate_mechanic.html', context)

@login_required
def add_junior_mechanic(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id)
    if request.method == 'POST':
        junior_mechanic_id = request.POST.get('junior_mechanic')
        junior_mechanic = get_object_or_404(Mechanic, id=junior_mechanic_id, status=MechanicStatus.ACTIVE)

        AllocateJuniorMechanics.objects.create(
            junior_mechanic=junior_mechanic.mechanic,
            senior_mechanic=request.user,
            slot=slot
        )

        junior_mechanic.status = MechanicStatus.WORKING
        junior_mechanic.save()

        return redirect('allocate_mechanic')

@login_required
def remove_junior_mechanic(request, slot_id, junior_mechanic_id):
    slot = get_object_or_404(Slot, id=slot_id)
    junior_mechanic = get_object_or_404(Mechanic, mechanic__id=junior_mechanic_id)
    
    allocation = get_object_or_404(AllocateJuniorMechanics, slot=slot, junior_mechanic=junior_mechanic.mechanic)
    allocation.delete()

    junior_mechanic.status = MechanicStatus.ACTIVE
    junior_mechanic.save()

    return redirect('allocate_mechanic')







#/////////Customer details in Admin Page/////////////////////////////

def customerdetails(request):

    customers = CustomUser.objects.filter(role='customer').select_related('details')
    return render(request,'admin/customerdetails.html',{'customers':customers})


def delete_customer(request, email):
    customer = get_object_or_404(CustomUser, email=email)
    if request.method == "POST":
        customer.delete()
        return redirect('customerdetails')
    return render(request, 'customerdetails')

#/////////Service Manager details in Admin Page/////////////////////////////


def service_manager_list(request):
    managers = CustomUser.objects.filter(role='service_manager')  # Filter service managers
    return render(request, 'admin/service_manager_list.html', {'managers': managers})

def delete_service_manager(request, email):
    manager = get_object_or_404(CustomUser, email=email, role='service_manager')
    if request.method == "POST":
        manager.delete()
        return redirect('service_manager_list')
    return redirect('service_manager_list')

def add_service_manager(request) :
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        details_form = UserDetailsForm(request.POST)
        if user_form.is_valid() and details_form.is_valid():
            user = user_form.save()
            details = details_form.save(commit=False)
            details.user = user
            details.save()
            messages.success(request, 'Registered Successfully.')
            return redirect('service_manager_list')  
    else:
        user_form = CustomUserCreationForm()
        details_form = UserDetailsForm()
    return render(request,"admin/add_service_manager.html",{'user_form': user_form, 'details_form': details_form})


#/////////Mechanics details in Admin Page/////////////////////////////


# def mechanic_list(request):
#     mechanics_users = CustomUser.objects.filter(role='mechanic')
#       # Filter service managers
#     mechanics_data = []

#     for user in mechanics_users:
#             print(user)
#             des =Mechanic.objects.filter(mechanic = user)
#             if(des):
#                 res =des
#             else:
#                 res=''
#             print(res)
#             mechanics_data.append({
#                 'mechanic': user,
#                 'data':res
#             })
#     print(mechanics_data)
#     return render(request, 'admin/mechanics_list.html', {'mechanics': mechanics_data})


def mechanic_list(request):
    mechanics_users = CustomUser.objects.filter(role='mechanic')
    mechanics_data = []

    for user in mechanics_users:
        mechanic_details = Mechanic.objects.filter(mechanic=user).first()
        user_details = UserDetails.objects.filter(user=user).first()
        
        mechanics_data.append({
            'mechanic': user,
            'data': mechanic_details,
            'details': user_details
        })

    return render(request, 'admin/mechanics_list.html', {'mechanics': mechanics_data})

# def delete_mechanic(request, email):
#     mechanic = get_object_or_404(CustomUser, email=email, role='mechanic')
#     if request.method == "POST":
#         mechanic.delete()
#         return redirect('mechanic_list')
#     return redirect('mechanic_list')

def delete_mechanic(request, email):
    mechanic = get_object_or_404(CustomUser, email=email, role='mechanic')
    mechanic.delete()  # Also removes related UserDetails due to cascade
    messages.success(request, 'Mechanic deleted successfully.')
    return redirect('mechanic_list')

def add_mechanic(request) :
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        details_form = UserDetailsForm(request.POST)
        if user_form.is_valid() and details_form.is_valid():
            user = user_form.save()
            details = details_form.save(commit=False)
            details.user = user
            details.save()
            messages.success(request, 'Registered Successfully.')
            return redirect('mechanic_list')  
    else:
        user_form = CustomUserCreationForm()
        details_form = UserDetailsForm()
    return render(request,"admin/add_mechanic.html",{'user_form': user_form, 'details_form': details_form})


# def mechanics_list(request):
#     mechanics = Mechanic.objects.all()
#     return render(request, 'mechanics_list.html', {'mechanics': mechanics})

# View for updating mechanic level
def update_mechanic_level(request, mechanic_id):
    mechanic_user = get_object_or_404(CustomUser, id=mechanic_id)
    
    # Check if the Mechanic entry exists for the user
    mechanic, created = Mechanic.objects.get_or_create(mechanic=mechanic_user)
    
    if request.method == 'POST':
        selected_level = request.POST.get('level')
        mechanic.level = selected_level
        mechanic.save()

        if created:
            messages.success(request, 'Mechanic created and level set successfully.')
        else:
            messages.success(request, 'Mechanic level updated successfully.')
        
        return redirect('mechanic_list')

    return redirect('mechanic_list')


def mechanic_profile(request, email):
    mechanic = get_object_or_404(CustomUser, email=email, role='mechanic')
    user_details = UserDetails.objects.get(user=mechanic)
    mechanic_data = Mechanic.objects.get(mechanic=mechanic)
    
    return render(request, 'admin/mechanic_profile.html', {
        'mechanic': mechanic,
        'user_details': user_details,
        'mechanic_data': mechanic_data
    })

def edit_mechanic_profile(request, mechanic_id):
    mechanic = get_object_or_404(CustomUser, id=mechanic_id)
    if request.method == 'POST':
        mechanic.details.name = request.POST.get('name')
        mechanic.details.phone = request.POST.get('phone')
        mechanic.details.address = request.POST.get('address')
        mechanic.details.city = request.POST.get('city')
        mechanic.details.place = request.POST.get('place')
        mechanic.details.pincode = request.POST.get('pincode')
        mechanic.details.save()
        return redirect('mechanic_profile', email=mechanic.email)



#////////////////////Service Categories Adding by admin///////////////////////////////////

def service_category_list(request):
    service_categories = ServiceCategory.objects.all()

    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('service_category_list')

    form = ServiceCategoryForm()

    return render(request, 'admin/service/service_category_list.html', {
        'service_categories': service_categories,
        'form': form
    })

def edit_service_category(request, pk):
    service_category = get_object_or_404(ServiceCategory, pk=pk)

    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, request.FILES, instance=service_category)
        if form.is_valid():
            form.save()
            return redirect('service_category_list')

    form = ServiceCategoryForm(instance=service_category)

    return render(request, 'admin/service/edit_service_category.html', {
        'form': form,
        'service_category': service_category
    })

def delete_service_category(request, pk):
    service_category = get_object_or_404(ServiceCategory, pk=pk)
    if request.method == 'POST':
        service_category.delete()
        messages.success(request, f'Service category "{service_category.name}" has been deleted.')
        return redirect('service_category_list')
    return render(request, 'admin/service/delete_service_category.html', {'service_category': service_category})

#///////////////////   Service Types by Admin ?////////////////////

# views.py


# View to display service types for a specific category
def service_type_list(request, category_id):
    category = get_object_or_404(ServiceCategory, pk=category_id)
    service_types = category.service_types.all()  # Fetch related service types
    
    # If the form is being submitted
    if request.method == 'POST':
        form = ServiceTypeForm(request.POST, request.FILES)
        if form.is_valid():
            service_type = form.save(commit=False)
            service_type.category = category
            service_type.save()
            messages.success(request, 'Service type added successfully.')
            return redirect('service_type_list', category_id=category_id)
    else:
        form = ServiceTypeForm()

    # Render the page with service types and the form for adding service types
    return render(request, 'admin/service/service_type_list.html', {
        'category': category,
        'service_types': service_types,
        'form': form  # Pass the form to the template
    })

# View to edit a service type
def edit_service_type(request, pk):
    service_type = get_object_or_404(ServiceType, pk=pk)
    if request.method == 'POST':
        form = ServiceTypeForm(request.POST, request.FILES, instance=service_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service type updated successfully.')
            return redirect('service_type_list', category_id=service_type.category.pk)
    else:
        form = ServiceTypeForm(instance=service_type)
    return render(request, 'admin/service/edit_service_type.html', {'form': form, 'service_type': service_type})

# View to delete a service type
def delete_service_type(request, pk):
    service_type = get_object_or_404(ServiceType, pk=pk)
    category_id = service_type.category.pk
    if request.method == 'POST':
        service_type.delete()
        messages.success(request, 'Service type deleted successfully.')
        return redirect('service_type_list', category_id=category_id)
    return render(request, 'admin/service/delete_service_type.html', {'service_type': service_type})


#////////////////////////////// Add   Service price ////////////////////////////////
def brands(request):
    vehicle_makes = VehicleMake.objects.all()
    return render(request, 'admin/service_price/brands.html', {'vehicle_makes': vehicle_makes})
def variants(request, make_id):
    variants = VehicleModel.objects.filter(make_id=make_id)
    return render(request, 'admin/service_price/variants.html', {'variants': variants})
from .models import ServiceCategory

def service_category(request, variant_id):
    service_categories = ServiceCategory.objects.all()
    vehicle_variant = get_object_or_404(VehicleModel, id=variant_id)
    return render(request, 'admin/service_price/service_category.html', {'service_categories': service_categories, 'vehicle_variant': vehicle_variant})

# def service_type(request, category_id, variant_id):
#     service_types = ServiceType.objects.filter(category_id=category_id)
#     vehicle_variant = get_object_or_404(VehicleModel, id=variant_id)
#     return render(request, 'admin/service_price/service_type.html', {'service_types': service_types, 'vehicle_variant': vehicle_variant})

def service_type(request, variant_id, category_id):
    vehicle_variant = get_object_or_404(VehicleModel, id=variant_id)
    service_types = ServiceType.objects.filter(category_id=category_id)

    # Prepare a dictionary to store service prices for each service type
    service_prices_dict = {}

    for service_type in service_types:
        # Filter based on the correct field 'vehicle_model' (variant)
        service_price = ServicePrice.objects.filter(vehicle_model=vehicle_variant, service_type=service_type).first()
        service_prices_dict[service_type.id] = service_price

    if request.method == 'POST':
        service_type_id = request.POST.get('service_type_id')
        price = request.POST.get('price')
        description = request.POST.get('description')

        service_type = get_object_or_404(ServiceType, id=service_type_id)

        # Check if a ServicePrice already exists for the selected vehicle variant and service type
        service_price, created = ServicePrice.objects.get_or_create(
            vehicle_model=vehicle_variant,
            service_type=service_type,
            defaults={'price': price, 'description': description}
        )

        if not created:
            # If it already exists, update the price and description
            service_price.price = price
            service_price.description = description
            service_price.save()

        # Redirect after saving to avoid form resubmission
        return redirect('service_type', variant_id=vehicle_variant.id, category_id=category_id)

    context = {
        'service_types': service_types,
        'vehicle_variant': vehicle_variant,
        'service_prices_dict': service_prices_dict,  # Pass the filtered prices
    }

    return render(request, 'admin/service_price/service_type.html', context)



# def add_service_price(request, service_type_id, variant_id):
#     service_type = get_object_or_404(ServiceType, id=service_type_id)
#     vehicle_variant = get_object_or_404(VehicleModel, id=variant_id)
    
#     if request.method == 'POST':
#         form = ServicePriceForm(request.POST)
#         if form.is_valid():
#             service_price = form.save(commit=False)
#             service_price.service_type = service_type
#             service_price.vehicle_model = vehicle_variant
#             service_price.save()
#             return redirect('service_type', category_id=service_type.category.id, variant_id=vehicle_variant.id)
#     else:
#         form = ServicePriceForm()
    
#     return render(request, 'admin/service_price/add_service_price.html', {'form': form, 'service_type': service_type, 'vehicle_variant': vehicle_variant})

def add_service_price(request, service_type_id, variant_id):
    service_type = get_object_or_404(ServiceType, id=service_type_id)
    vehicle_variant = get_object_or_404(VehicleModel, id=variant_id)
    
    if request.method == 'POST':
        form = ServicePriceForm(request.POST)
        if form.is_valid():
            service_price = form.save(commit=False)
            # Set the foreign keys
            service_price.service_type = service_type
            service_price.vehicle_model = vehicle_variant
            service_price.save()
            return redirect('service_type', category_id=service_type.category.id, variant_id=vehicle_variant.id)
    else:
        form = ServicePriceForm()
    
    return render(request, 'admin/service_price/add_service_price.html', {'form': form, 'service_type': service_type, 'vehicle_variant': vehicle_variant})



# def edit_service_price(request, service_price_id):
#     # Get the service price object or return a 404 if not found
#     service_price = get_object_or_404(ServicePrice, id=service_price_id)
    
#     if request.method == 'POST':
#         form = ServicePriceForm(request.POST, instance=service_price)  # Bind the form to the existing service price
#         if form.is_valid():
#             form.save()  # Save the updated service price
#             return redirect('service_type', category_id=service_price.service_type.category.id, variant_id=service_price.vehicle_model.id)  # Redirect to the service type page
#     else:
#         form = ServicePriceForm(instance=service_price)  # Pre-fill the form with existing data
    
#     return render(request, 'admin/service_price/edit_service_price.html', {'form': form, 'service_price': service_price})

def edit_service_price(request, service_price_id):
    service_price = get_object_or_404(ServicePrice, id=service_price_id)
    
    if request.method == 'POST':
        form = ServicePriceForm(request.POST, instance=service_price)  # Bind to existing service price
        if form.is_valid():
            form.save()  # Save the updated service price
            return redirect('service_type', category_id=service_price.service_type.category.id, variant_id=service_price.vehicle_model.id)
    else:
        form = ServicePriceForm(instance=service_price)  # Pre-fill form with existing data
    
    return render(request, 'admin/service_price/edit_service_price.html', {'form': form, 'service_price': service_price})


@login_required(login_url='customerLogin')
def receive_complaint(request):
    if request.method == 'POST':
        complaint_text = request.POST.get('complaint')
        if complaint_text:
            # Save the complaint to the database
            CustomerComplaint.objects.create(user=request.user, complaint=complaint_text)
            message = "Your complaint has been submitted successfully."
        else:
            message = "Please fill out the complaint field."
        return render(request, 'index.html', {'message': message})
    
    return render(request, 'submit_complaint.html')

@login_required
def complaint_list(request):
    complaints = CustomerComplaint.objects.all()
    return render(request, 'complaint_list.html', {'complaints': complaints})



#//////////////   Job Portal /////////////////////////


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import JobPost, JobApplication
from .form import JobPostForm, JobApplicationForm

@login_required
def post_job(request):
    # if request.user.role != 'service_manager':  # Only mechanics can post jobs
    #     return redirect('job_list')
    
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user  # Mechanic is posting the job
            job.save()
            return redirect('manager_job_list')
    else:
        form = JobPostForm()
    return render(request, 'serviceManager/post_job.html', {'form': form})


def manager_job_list(request):
    jobs = JobPost.objects.filter(is_active=True)
    return render(request, 'serviceManager/manager_job_list.html', {'jobs': jobs})
def job_list(request):
    jobs = JobPost.objects.filter(is_active=True)
    return render(request, 'jobportal/job_list.html', {'jobs': jobs})

def apply_job(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    if not job.is_active:
        return render(request, 'jobportal/job_closed.html')

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.save()
            messages.success(request, 'You have successfully applied for the job.')
            return redirect('job_list')
    else:
        form = JobApplicationForm()
    return render(request, 'jobportal/apply_job.html', {'form': form, 'job': job})
# from django.contrib import messages
# from django.shortcuts import redirect, render, get_object_or_404
# from .models import JobPost
# from .form import JobApplicationForm

# def apply_job(request, job_id):
#     job = get_object_or_404(JobPost, id=job_id)
    
#     # Check if the job is still active
#     if not job.is_active:
#         return render(request, 'jobportal/job_closed.html')

#     if request.method == 'POST':
#         form = JobApplicationForm(request.POST, request.FILES)
#         if form.is_valid():
#             application = form.save(commit=False)
#             application.job = job
#             application.save()

#             # Add a success message
#             messages.success(request, 'You have successfully applied for the job.')

#             # Redirect to the job list page
#             return redirect('job_list')
#     else:
#         form = JobApplicationForm()

#     return render(request, 'jobportal/apply_job.html', {'form': form, 'job': job})



@login_required
def view_candidates(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    
    # Ensure only the service manager who posted the job can view the candidates
    if request.user.role != 'service_manager' or job.posted_by != request.user:
        return redirect('job_list')

    applications = JobApplication.objects.filter(job=job)
    return render(request, 'serviceManager/select_candidate.html', {
        'job': job,
        'applications': applications
    })


from django.contrib.auth.models import AbstractBaseUser

@login_required
def select_candidate(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)

    # Check if the logged-in user is the service manager who posted the job
    if request.user.role != 'service_manager' or application.job.posted_by != request.user:
        return redirect('job_list')  # Redirect if unauthorized access
    
    # Mark candidate as selected
    application.is_selected = True
    application.save()

    # Deactivate the job once a candidate is selected
    application.job.is_active = False
    application.job.save()

    
    # Create a user account for the selected candidate
    # User = get_user_model()
    # random_password = AbstractBaseUser().make_random_password()  # Generate random password
    # user = User.objects.create_user(
    #     email=application.candidate_email,
    #     password=random_password,
    #     role='CANDIDATE'
    # )

    # Redirect to the job list after selecting a candidate
    return redirect('manager_job_list')



# @login_required
# def select_candidate(request, application_id):
#     application = get_object_or_404(JobApplication, id=application_id)

#     # Check if the logged-in user is the service manager who posted the job
#     if request.user.role != 'service_manager' or application.job.posted_by != request.user:
#         return redirect('job_list')  # Redirect if unauthorized access
    
#     # Mark candidate as selected
#     application.is_selected = True
#     application.save()

#     # Deactivate the job once a candidate is selected
#     application.job.is_active = False
#     application.job.save()

#     # Create a user account for the selected candidate
#     User = get_user_model()
#     user = User.objects.create_user(
#         email=application.candidate_email,
#         password=User.objects.make_random_password(),
#         role='CANDIDATE'
#     )

#     # Redirect to the job list after selecting a candidate
#     return redirect('manager_job_list')





# @login_required
# def select_candidate(request, application_id):
#     application = get_object_or_404(JobApplication, id=application_id)
    
#     if request.user.role != 'service_manager' or application.job.posted_by != request.user:
#         return redirect('job_list')  # Only the mechanic who posted the job can select a candidate

#     application.is_selected = True
#     application.save()

#     # Deactivate the job post once a candidate is selected
#     application.job.is_active = False
#     application.job.save()

#     # Create user account for the selected candidate
#     User = get_user_model()
#     user = User.objects.create_user(
#         email=application.candidate_email,
#         password=User.objects.make_random_password(),
#         role='CANDIDATE'  # Candidate role
#     )




#     # Send email to the candidate
#     send_mail(
#         'Job Application Accepted',
#         f'You have been selected for the job {application.job.title}. '
#         f'Login with your email: {application.candidate_email}.',
#         'noreply@jobportal.com',
#         [application.candidate_email],
#         fail_silently=False
#     )

#     return redirect('job_applications_list', job_id=application.job.id)

# from django.conf import settings
# def sendit():
#     subject = 'Welcome To AutoMech' 
#     message = 'dsafsrdgdsghsdhgfshjfgsj' 
#     from_email = settings.DEFAULT_FROM_EMAIL 
#     recipient_list = ['shejinvj274@gmail.com'] 
#     send_mail(subject, from_email, recipient_list,message)
