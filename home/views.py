from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now, timedelta
from django.db.models import Sum, Count, Avg
from django.views.decorators.csrf import csrf_exempt  
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
import json
import random
import requests
import razorpay
from django.db.models import Q

from .models import (
    Category, Product, Cart, Subcategory, Wishlist, Banner, Order, 
    UserProfile, Review, Size, Address, Payment, OrderItem, 
    Feedback, Coupon, Subscriber,User
)


from .form import (
    ReviewForm, AddressForm, UserProfileForm, 
    RegistrationForm, FeedbackForm
)

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def home(request):
    categories = Category.objects.all()
    items = Product.objects.all()[:4]
    
    banners = Banner.objects.filter(active_status=True)
    reviews = Review.objects.select_related('user', 'product').all()
    
    usd_inr = fetch_inr_rate()  

    if isinstance(usd_inr, str):  
        return render(request, "home.html", {"error": "INR rate fetch failed!"})

   
    gold_24k = fetch_metal_rate("XAU")
    silver_rate = fetch_metal_rate("XAG")

    
    gold_22k = round(gold_24k * 0.916, 2) if isinstance(gold_24k, (int, float)) else "Error"
    
    return render(request, 'index.html', {
        'categories': categories,
        'items': items,
        'banners': banners,
        'reviews': reviews,
        "gold_24k": gold_24k,
        "gold_22k": gold_22k,
        "silver_rate": silver_rate,
        "usd_inr": usd_inr
    })




def category_products(request, subcategory_slug):
    subcategory = get_object_or_404(Subcategory, slug=subcategory_slug)
    products = Product.objects.filter(category=subcategory.category)
    return render(request, 'shop-categories-top.html', {'subcategory': subcategory, 'products': products})

def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    items = Product.objects.all()
    feedback_list = Feedback.objects.filter(product=product).order_by('-created_at')
    reviews = Review.objects.filter(product=product) 


    if not reviews.exists():
        reviews = Review.objects.none()

    rating_summary = reviews.aggregate(avg_rating=Avg('rating'), total_reviews=Count('id'))
    avg_rating = round(rating_summary['avg_rating'] or 0, 1)
      # Round to 1 decimal place
    total_reviews = rating_summary['total_reviews']

    # Count the number of reviews for each rating (1 to 5 stars)
    rating_counts = reviews.values('rating').annotate(count=Count('rating')).order_by('-rating')
    rating_distribution = {i: 0 for i in range(1, 6)}  # Initialize 1-5 ratings to 0

    for rate in rating_counts:
        rating_distribution[rate['rating']] = rate['count']

    # Calculate the percentage width of rating bars
    rating_percentages = {i: (rating_distribution[i] / total_reviews * 100) if total_reviews else 0 for i in range(1, 6)}\
    
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Your review has been submitted successfully.")
            return redirect('product_detail', product_slug=product.slug)
    else:
        form = ReviewForm()

                

    total_reviews = reviews.count()
    sizes = Size.objects.filter(product=product)  # Fetch sizes for this product
    if not product.short_description:
        product.short_description = product.generate_short_description()
        product.save()
    
    if not product.long_description:
        product.long_description = product.generate_long_description()
        product.save()

    context = {
        'product': product,
        'short_description': product.short_description,
        'long_description': product.long_description,
        'items': items,
        "sizes": sizes,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'feedback_list': feedback_list,
        'avg_rating': int(avg_rating),  # ✅ Convert to int in views.py
        'total_reviews': int(total_reviews),
        'rating_distribution': rating_distribution,
        'rating_percentages': rating_percentages,
        'form': form,
    }
 
    return render(request, 'product-detail.html',context)

def subcategory(request,subcategory_slug):
    
    subcategory = get_object_or_404(Subcategory, slug=subcategory_slug)
    products = Product.objects.filter(subcategory=subcategory)  
    return render(request, 'product1.html', {'subcategory': subcategory, 'products': products})
    


def user_login(req):
    if req.method == "POST":
        try:
            username = req.POST.get('username')
            password = req.POST.get('password')
            
            # Authenticate the user using Django's authenticate function
            user_obj = authenticate(req, username=username, password=password)
            print(user_obj)
            if user_obj is not None:
                login(req, user_obj)  # Correct login method
                return redirect('/profile')  # Redirect to home or any other page
            else:
                # Authentication failed
                messages.error(req, "Wrong username or password!")
                return redirect('/login/')
        
        except Exception as e:
            messages.error(req, f"Something went wrong: {e}")
            return redirect('/login/')
    
    return render(req, "accounts/login.html")






def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after registration
            messages.success(request, "Registration successful. Welcome!")
            return redirect("login")  # Redirect to login page
        else:
            print(form.errors)  # Debugging: Print form errors in the terminal
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login')

    
def forget(request):
    return render(request,'accounts/forget-password.html')



def product_from_cart(user):
    """Fetch all products from the cart for the logged-in user."""
    if not user.is_authenticated:
        return []  # If the user is not authenticated, return an empty list

    try:
        # Filter the cart to get products related to the logged-in user
        cart_items = Cart.objects.filter(user=user)
        products_in_cart = [cart_item.product for cart_item in cart_items]
        return products_in_cart 
    except Exception as e:
        return []



from decimal import Decimal, ROUND_HALF_UP

def cart_page(req):
    if not req.user.is_authenticated:
        return redirect('login')

    products = product_from_cart(req.user)
    items = Product.objects.all()
    shipping_cost = 0  
    subtotal = sum(Decimal(product.price) for product in products)
    subtotal = Decimal(subtotal).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    discount = Decimal(0)
    if subtotal > Decimal(50000):  # Ensure comparison is done using Decimal
        discount = (subtotal * Decimal("0.1")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        shipping_cost = Decimal(0)

    
    total = (subtotal - discount + shipping_cost).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    return render(req, "shopping-cart.html", {
        "products": products,
        "items": items, 
        "subtotal": subtotal,
        "discount": discount,
        "shipping_cost": shipping_cost,
        "total": total
    })



def add_to_cart(req, getid):
    """Add a product to the cart based on product ID."""
    if not req.user.is_authenticated:
        return redirect('login')  # Redirect to login if the user is not authenticated

    # Fetch the product by ID
    product = get_object_or_404(Product, id=getid)
    

    # Check if the product is already in the cart for the user
    cart_item, created = Cart.objects.get_or_create(
        user=req.user,
        product=product,
        defaults={"quantity": 1}
    )

    if not created:
        # iIf the product is already in the cart, increase the quantity
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_page')  # Redirect to the home page after adding the product
  

def remove_from_cart(request, getid):
    """Remove a product from the cart."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "User not authenticated"}, status=401)

    cart_item = get_object_or_404(Cart, user=request.user, product_id=getid)
    cart_item.delete()  # ✅ This actually removes the item from the database

    return JsonResponse({"success": True, "message": "Item removed successfully"})


def category_view(req, slug):
    selected_category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=selected_category)
    subcategories = selected_category.subcategories.all()  

    return render(req, 'shop-categories-top.html', {'top': [selected_category], 'products': products, 'subcategories': subcategories})

def add_to_wishlist(request, product_id):
    """Add a product to the wishlist if not already added."""
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if the user is not authenticated

    product = get_object_or_404(Product, id=product_id)

    # Check if the product is already in the wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if created:
        messages.success(request, "Product added to your wishlist!")
    else:
        messages.info(request, "Product is already in your wishlist!")

    return redirect('wishlist')





def remove_from_wishlist(request, product_id):
    """Remove a product from the wishlist."""
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if the user is not authenticated

    product = get_object_or_404(Product, id=product_id)
    
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        messages.success(request, "Product removed from your wishlist.")
    except Wishlist.DoesNotExist:
        messages.error(request, "Product is not in your wishlist.")

    return redirect('wishlist')

def wishlist(request):
    if not request.user.is_authenticated:
        return redirect('login')  
    
    # Get all products in the wishlist for the logged-in user
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    return render(request, 'wish-list.html', {'wishlist_items': wishlist_items})





def blog(req):
    return render(req,'blog/blog.html')

def blog1(req):
    return render(req,'blog/blog1.html')

def blog2(req):
    return render(req,'blog/blog2.html')

def blog3(req):
    return render(req,'blog/blog3.html')

def blog4(req):
    return render(req,'blog/blog4.html')

def blog5(req):
    return render(req,'blog/blog5.html')

def blog6(req):
    return render(req,'blog/blog6.html')



def productGrid(req):
    items = Product.objects.all()
    return render(req,'shop-default-grid.html',{'items': items})


@login_required
def checkout(request):
    # Fetch addresses, coupons, and cart items
    user_profile = UserProfile.objects.filter(user=request.user).first()
    addresses = Address.objects.filter(user=request.user).order_by("-is_default", "-id")
    default_address = addresses.first()
    coupons = Coupon.objects.filter(is_active=True)
    cart_items = Cart.objects.filter(user=request.user)

    # Redirect if cart is empty
    if not cart_items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect("cart_page")

    # Fetch the user's profile
    userprofile = UserProfile.objects.filter(user=request.user).first()

    # Calculate subtotal, discount, and total
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    discount = Decimal(0)
    total = subtotal - discount

    if request.method == "POST":
        try:
            total_price = Decimal(request.POST.get("total_price"))
        except (TypeError, ValueError):
            messages.error(request, "Invalid total price!")
            return redirect("checkout")

        if default_address:
            # Create Order
            order = Order.objects.create(
                user=request.user, 
                address=default_address, 
                total_price=total_price
            )

            # Save Order Items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )

            # Create Payment Entry
            Payment.objects.create(
                user=request.user,
                order=order,
                amount=total_price,
                status="Pending"  # Set to "Completed" after payment success
            )

            # Clear cart after successful order
            cart_items.delete()

            messages.success(request, "Order placed successfully!")
            return redirect("orders")
        else:
            messages.error(request, "No valid address found!")

        request.session["total_price"] = str(total)
        request.session["address"] = default_address.id if default_address else None

    context = {
         "userprofile": user_profile,
        "addresses": addresses,
        "default_address": default_address,
        "cart_items": cart_items,
        "subtotal": subtotal,
        "discount": discount,
        "total": total,
        "coupons": coupons,
        "userprofile": userprofile,
        "razorpay_key": settings.RAZORPAY_KEY_ID 
    }

    return render(request, "checkout.html", context)

def term(request):
    return render(request,'term-of-use.html')

 


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Fetch user's default address
    default_address = Address.objects.filter(user=request.user, is_default=True).first()

    if request.method == "POST":
        # Update user fields
        request.user.first_name = request.POST.get("first_name", request.user.first_name)
        request.user.last_name = request.POST.get("last_name", request.user.last_name)
        request.user.email = request.POST.get("email", request.user.email)
        request.user.save()

        # Update user profile fields
        user_profile.phone = request.POST.get("phone", user_profile.phone)
        user_profile.save()

        # Update or create address entry
        if default_address:
            default_address.street_address = request.POST.get("address", default_address.street_address)
            default_address.city = request.POST.get("city", default_address.city or "")
            default_address.state = request.POST.get("state", default_address.state or "")
            default_address.pincode = request.POST.get("pincode", default_address.pincode or "")
            default_address.country = request.POST.get("country", default_address.country or "")
            default_address.save()
        else:
            # Create new address if not found
            Address.objects.create(
                user=request.user,
                street_address=request.POST.get("address"),
                city=request.POST.get("city", ""),
                state=request.POST.get("state", ""),
                pincode=request.POST.get("pincode", ""),
                country=request.POST.get("country", ""),
                is_default=True
            )

        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, "accounts/my-account.html", {
        "user_profile": user_profile,
        "default_address": default_address
    })

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in after changing password
            messages.success(request, "Your password has been successfully updated.")
            return redirect("profile")  # Change to your profile page URL name
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/my-account.html", {"password_form": form})

def adress(request):
    addresses = Address.objects.filter(user=request.user)
    
    return render(request, "accounts/address.html", {"addresses": addresses})





@login_required
def add_address(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")  # Fix: use full_name instead of first_name
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        street_address = request.POST.get("street_address")  # Fix: match the model field name
        city = request.POST.get("city")
        state = request.POST.get("state")
        postal_code = request.POST.get("postal_code")
        country = request.POST.get("country")
        is_default = request.POST.get("is_default") == "on"

        # Save address to database with correct field names
        address = Address.objects.create(
            user=request.user,
            full_name=full_name,  # Fix: use full_name instead of first_name
            last_name=last_name,
            email=email,
            phone=phone,
            street_address=street_address,  # Fix: use street_address instead of address
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            is_default=is_default
        )

        # If set as default, remove default from other addresses
        if is_default:
            Address.objects.filter(user=request.user).exclude(id=address.id).update(is_default=False)

        print("Address saved successfully!")  # Debugging

        return redirect("address")

    addresses = Address.objects.filter(user=request.user)  
    return render(request, "accounts/address.html", {"addresses": addresses})






          
    

def payment_success(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get("razorpay_payment_id")
            order_id = request.POST.get("razorpay_order_id")
            signature = request.POST.get("razorpay_signature")

            print(f"🔹 Payment ID: {payment_id}, Order ID: {order_id}, Signature: {signature}")

            # ✅ Verify Razorpay payment
            result = razorpay_client.utility.verify_payment_signature({
                "razorpay_payment_id": payment_id,
                "razorpay_order_id": order_id,
                "razorpay_signature": signature
            })

            if not result:
                return JsonResponse({"status": "failed", "message": "Payment verification failed!"})

            total_price = request.session.get("total_price")
            address_id = request.session.get("address")

            if not total_price or not address_id:
                return JsonResponse({"status": "failed", "message": "Session data missing!"})

            address = Address.objects.get(id=address_id)

            # ✅ Check if order exists
            new_order, created = Order.objects.get_or_create(
                user=request.user,
                address=address,
                defaults={
                    "total_price": total_price,
                    "status": "Paid",
                    "tracking_no": "ORD" + str(random.randint(10000, 99999)),
                    "razorpay_order_id": order_id
                }
            )

            # ✅ Ensure payment is saved
            payment, payment_created = Payment.objects.get_or_create(
                order=new_order,
                defaults={
                    "user": request.user,
                    "amount": total_price,
                    "payment_method": "Razorpay",
                    "payment_status": "Completed"
                }
            )

            if not payment_created:
                payment.payment_status = "Completed"
                payment.save()

            # ✅ Clear cart and session
            Cart.objects.filter(user=request.user).delete()
            request.session.pop("total_price", None)
            request.session.pop("address", None)

            return JsonResponse({"status": "success", "order_id": new_order.id, "payment_id": payment.id})

        except Exception as e:
            return JsonResponse({"status": "failed", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request method."})

@csrf_exempt
def subscribe(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse({"message": "⚠️ Email is required!"}, status=400)

            # Check if already subscribed
            if Subscriber.objects.filter(email=email).exists():
                return JsonResponse({"message": "✅ You're already subscribed!"}, status=400)

            # Save the subscriber
            Subscriber.objects.create(email=email)

            # Email Content
            subject = "🎉 Welcome to Our Newsletter!"
            message = """
            <html>
            <body style="font-family: Arial, sans-serif; text-align: center;">
                <h2 style="color: #4CAF50;">Thank You for Subscribing! 🎉</h2>
                <p>We appreciate you joining our newsletter. Stay tuned for exclusive updates, offers, and promotions.</p>
                <p>💎 Get ready for the best deals on jewelry!</p>
                <p style="margin-top: 20px;"><strong>Best Regards, <br> HariOm Team</strong></p>
            </body>
            </html>
            """

            # Send Confirmation Email
            send_mail(
                subject,
                "",  # Empty text message since we are using HTML email
                settings.EMAIL_HOST_USER,  # Sender email (from settings)
                [email],  # Recipient email
                fail_silently=False,
                html_message=message,  # Styled HTML email
            )

            return JsonResponse({"message": "🎉 Thank you for subscribing! Check your email 📩"}, status=200)

        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

    return JsonResponse({"message": "Invalid request!"}, status=400)

def faq(req):
    return render(req,'FAQs.html')

def about(req):
    return render(req,'about-us.html')

def apply_coupon(request):
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        total_amount = float(request.POST.get("total_amount", 0))
        
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            if total_amount >= coupon.min_order_amount:
                discount = (coupon.discount_percentage / 100) * total_amount
                return JsonResponse({"success": True, "discount": round(discount, 2)})
            else:
                return JsonResponse({"success": False, "message": "Order amount too low for this coupon."})
        except Coupon.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invalid coupon code."})
    
    return JsonResponse({"success": False, "message": "Invalid request."})


def placeorder(request):
    if request.method == 'POST':
        currentuser = User.objects.get(id=request.user.id)

        # ✅ Save user details if missing
        if not currentuser.first_name:
            currentuser.first_name = request.POST.get('fname')
            currentuser.last_name = request.POST.get('lname')
            currentuser.save()

        # ✅ Save user profile if it does not exist
        UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "phone": request.POST.get('phone'),
                "address": request.POST.get('address'),
                "city": request.POST.get('city'),
                "state": request.POST.get('state'),
                "country": request.POST.get('country'),
                "pincode": request.POST.get('pincode')
            }
        )

        # ✅ Generate a unique tracking number
        trackno = 'ORD' + str(random.randint(10000, 9999999))
        while Order.objects.filter(tracking_no=trackno).exists():
            trackno = 'ORD' + str(random.randint(10000, 9999999))

        # ✅ Calculate total price before creating the order
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        # ❗️ Ensure total price is not NULL
        if total_price is None or total_price <= 0:
            return JsonResponse({'status': 'failed', 'message': 'Invalid total price!'})

        # ✅ Create new order with total_price
        neworder = Order.objects.create(
            user=request.user,
            fname=request.POST.get('fname'),
            lname=request.POST.get('lname'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            country=request.POST.get('country'),
            pincode=request.POST.get('pincode'),
            payment_mode=request.POST.get('payment_mode'),
            tracking_no=trackno,
            total_price=total_price  # ✅ Set total_price here
        )

        # ✅ Save order items
        for item in cart_items:
            OrderItem.objects.create(
                order=neworder,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )
            # Decrease product stock
            item.product.quantity -= item.quantity
            item.product.save()

        # ✅ Handle Payment (If Razorpay)
        payment_id = request.POST.get('payment_id')

        if neworder.payment_mode.lower() == "paid by razorpay":
            if payment_id:
                Payment.objects.create(
                    user=request.user,
                    order=neworder,
                    amount=total_price,
                    payment_method="Razorpay",
                    payment_status="Completed",
                    payment_date=now()
                )
                neworder.payment_id = payment_id  # ✅ Save payment ID in Order model
                neworder.status = "Paid"
                neworder.save()
            else:
                print("❌ Error: Payment ID missing for Razorpay order!")

        # ✅ Clear cart after order
        cart_items.delete()

        # ✅ Redirect based on payment method
        if neworder.payment_mode.lower() == "paid by razorpay":
            return JsonResponse({
                'status': "Your order has been successfully placed.",
                'redirect_url': '/order/'
            })

        messages.success(request, "Your order has been placed successfully")
        return redirect('/order/')



def calculate_cart_total(user):
    cart_items = Cart.objects.filter(user=user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return total


    
@login_required
def razorpaycheck(request):
    cart_total = calculate_cart_total(request.user)  # Implement this function to sum cart items
    shipping = 50  # Fixed shipping cost

    # Retrieve the discount from the session or set to 0 if not available
    discount = request.session.get('discount', 0)

    final_total = cart_total + shipping - discount

    # Ensure the final total is not negative
    if final_total < 0:
        final_total = 0

    # Convert to paise for Razorpay
    amount_in_paise = int(final_total * 100)

    return JsonResponse({
        'total_price': amount_in_paise
    })

@login_required
def submit_feedback(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.product = product
            feedback.save()
            return redirect('productDetail', product_slug=product.slug)  # Use slug here
    else:
        form = FeedbackForm()
    return render(request, 'product-detail.html', {'form': form, 'product': product})

@login_required
def  my_orders(request):
    orders = Order.objects.filter(user=request.user)
    context = {'orders': orders}
    return render(request, "accounts/order.html", context)





@login_required
def orderdetail(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'accounts/order-detail.html', {
        'order': order, 
        'order_items': order_items
    })
   
def get_order_tracking(request, tracking_no):
    try:
        order = Order.objects.get(tracking_no=tracking_no)
        data = {
            "status": order.status,
            "shipped_time": order.shipped_time.strftime('%Y-%m-%d %H:%M:%S') if order.shipped_time else "Pending",
            "out_for_delivery_time": order.out_for_delivery_time.strftime('%Y-%m-%d %H:%M:%S') if order.out_for_delivery_time else "Pending",
            "delivered_time": order.delivered_time.strftime('%Y-%m-%d %H:%M:%S') if order.delivered_time else "Pending",
        }
        return JsonResponse(data)
    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)

import requests
from django.core.cache import cache
from django.shortcuts import render

# API URLs
GOLD_API_URL = "https://www.goldapi.io/api/"
EXCHANGE_API = "https://api.exchangerate-api.com/v4/latest/USD"  # Free Exchange API

# API Key (Replace with your valid Gold API Key)
API_KEY = "goldapi-apv72wsm7iwmcq9-io"

# Caching Timeouts
EXCHANGE_CACHE_TIME = 3600  # 1 hour
METAL_CACHE_TIME = 1800  # 30 minutes

def fetch_inr_rate():
    """Fetches USD to INR exchange rate and caches it for 1 hour."""
    cache_key = "usd_inr_rate"
    cached_rate = cache.get(cache_key)

    if cached_rate:
        return cached_rate  # Use cached rate if available

    response = requests.get(EXCHANGE_API)
    
    if response.status_code == 200:
        data = response.json()
        inr_rate = data["rates"].get("INR", 0)  # Fetch INR rate
        cache.set(cache_key, inr_rate, timeout=EXCHANGE_CACHE_TIME)  # Cache for 1 hour
        return inr_rate

    return 0  # Return 0 if fetch fails (prevents errors)


def fetch_metal_rate(metal):
    """Fetches gold or silver rate in INR and caches for 30 minutes."""
    cache_key = f"{metal}_rate"
    cached_rate = cache.get(cache_key)

    if cached_rate:
        return cached_rate  # Use cached value if available

    url = f"{GOLD_API_URL}{metal}/INR"  # Fetch directly in INR
    headers = {
        "x-access-token": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        price_per_ounce = data.get("price", 0)
        price_per_gram = price_per_ounce / 31.1035  # Convert ounce to gram
        price_per_10_grams = round(price_per_gram * 10, 2)  # Convert to 10 grams

        cache.set(cache_key, price_per_10_grams, timeout=METAL_CACHE_TIME)  # Cache for 30 minutes
        return price_per_10_grams

    return 0  # Return 0 if fetch fails


def get_gold_silver_rates():
    """Fetches both gold and silver rates in INR."""
    gold_rate = fetch_metal_rate("XAU")
    silver_rate = fetch_metal_rate("XAG")
    
    return gold_rate, silver_rate



 # Import your Category model

def search_results(request):
    query = request.GET.get('q', '')
    
    # Search across multiple fields and categories
    results = Product.objects.filter(
        Q(name__icontains=query) |
        Q(short_description__icontains=query) |
        Q(long_description__icontains=query) |
        Q(category__name__icontains=query)  # Search by category name
    ).distinct()
    
    # Get all categories that match the search
    category_results = Category.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    ).distinct()
    
    return render(request, 'search_results.html', {
        'results': results,
        'category_results': category_results,
        'query': query
    })