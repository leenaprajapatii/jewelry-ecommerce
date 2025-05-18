from home.models import Category ,Cart # Ensure 'home' is the correct app name

def categories_processor(request):
    categories = Category.objects.prefetch_related('subcategories').all()
    return {'categories': categories}

# from .utils import get_metal_rates

# def metal_rates(request):
#     return get_metal_rates()  # Returns {"gold_rate": ..., "silver_rate": ...}


def total_product_in_cart(request):
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
    else:
        cart_count = 0  # Show 0 if user is not logged in

    return {'added_product': cart_count}