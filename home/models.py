from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils.timezone import now



class Banner(models.Model):
    
    discount = models.IntegerField()
    image = models.ImageField(upload_to='banners/')
    active_status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.discount}%"

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.IntegerField()
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateField()

    def is_valid(self):
        """Check if the coupon is valid (active and not expired)."""
        return self.is_active and self.expiry_date >= now().date()


    def __str__(self):
        return f"{self.code} - {self.discount_percentage}%"

class Size(models.Model):  # Renamed 'size' to 'Size' for consistency
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name




class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='subcategory_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)



    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)  # SKU field
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True)
    quantity = models.IntegerField(default=0) 
    
    purity = models.CharField(max_length=50, blank=True, null=True)  
    material = models.CharField(max_length=50, choices=[('gold', 'Gold'), ('silver', 'Silver'), ('diamond', 'Diamond')], default='gold')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2)  # Weight in grams
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    hover_image = models.ImageField(upload_to='products/hover_images/', blank=True, null=True)
    sizes = models.ManyToManyField(Size, blank=True)  # 🔹 Many-to-Many Relationship
    average_rating = models.FloatField(default=0.0) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    short_description = models.TextField(blank=True)  # For top section
    long_description = models.TextField(blank=True)   # For detailed section

    def generate_short_description(self):
        return f"Elegant {self.purity or self.material} {self.category} designed for beauty and comfort."

    def generate_long_description(self):
        base_description = f"Introducing the {self.purity or self.material} {self.category}, a symbol of elegance and timeless sophistication. "

        material_desc = {
            "gold": "Crafted from the finest gold, this piece radiates warmth, prosperity, and a golden glow that never fades. Each curve and contour reflects the craftsmanship of master artisans, ensuring a creation as eternal as love itself. ",
            "silver": "Sculpted from pure sterling silver, this piece exudes understated elegance. A vision of celestial brilliance, silver has long been cherished for its purity and grace, making this an accessory fit for royalty. ",
            "diamond": "Encrusted with dazzling, ethically sourced diamonds, this jewelry piece captures light from every angle, mirroring the brilliance of the stars in the night sky. A masterpiece of radiance, it is designed to be cherished for generations. ",
            "platinum": "Forged from rare, luminous platinum, this jewelry piece represents strength, rarity, and everlasting beauty. A treasure that withstands the test of time, it carries an aura of prestige and grandeur. ",
        }.get(self.material, "")

        type_desc = {
            "ring": "A ring is more than an ornament—it is a promise, a memory, and a statement of individuality. Whether chosen for an engagement, a milestone, or a simple indulgence in luxury, this ring is a breathtaking representation of love and legacy. ",
            "bracelet": "Gracefully encircling the wrist, this bracelet is an emblem of refinement. Its fluid design adapts seamlessly to both contemporary and vintage styles, making it the perfect companion for every occasion. ",
            "necklace": "Draping effortlessly along the neckline, this necklace enhances your radiance with its exquisite charm. Whether layered for a bold statement or worn alone for an air of understated luxury, it is a masterpiece in itself. ",
            "earrings": "Each pair of earrings tells a story of elegance and allure. Whether chosen to complement an evening gown or to add a sparkle to your daily ensemble, these earrings redefine sophistication. ",
            "pendant": "Suspended delicately, this pendant carries not just its beauty but the stories and emotions it represents. An exquisite blend of artistry and meaning, it is a keepsake of memories and dreams. ",
        }.get(self.category, "")

        extra_details = (
            "Designed with an unwavering commitment to excellence, this piece is more than jewelry—it is an heirloom in the making. "
            "Perfectly suited for grand celebrations, romantic moments, or simply as a daily indulgence, it embodies luxury at its finest."
        )

        return base_description + material_desc + type_desc + extra_details

    # Auto-generate descriptions when saving
    def save(self, *args, **kwargs):
        if not self.short_description:
            self.short_description = self.generate_short_description()
        if not self.long_description:
            self.long_description = self.generate_long_description()
        if not self.sku:
            self.sku = f"SKU-{str(self.id).zfill(8)}"
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_sizes_list(self):
        return [size.name for size in self.sizes.all()]

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"SKU-{self.id or ''}".zfill(8)
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def update_average_rating(self):  # 🔹 Function to update average rating
        reviews = self.reviews.all()
        if reviews.exists():
            self.average_rating = sum([review.rating for review in reviews]) / reviews.count()
        else:
            self.average_rating = 0.0
        self.save()

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 🔹 Linked to User model
    title = models.CharField(max_length=255,default="No Title")
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='review_images/', blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):  # 🔹 Auto-update product rating when a review is saved
        super().save(*args, **kwargs)
        self.product.update_average_rating()

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

class ProductImage(models.Model):  # 🔹 Extra images for each product
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/multiple_images/')

    def __str__(self):
        return f"Image for {self.product.name}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Set null=False if user is mandatory
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=100,default="Not Available", blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100,default="Not Available", blank=True, null=True)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.product.name} (x{self.quantity})"


class Order(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Set null=False if user is mandatory
    fname = models.CharField(max_length=150,default='fname', null=False)
    lname = models.CharField(max_length=150,default='lname', null=False)
    email = models.CharField(max_length=150,default='email', null=False)
    phone = models.CharField(max_length=150,default='0', null=False)
    address = models.TextField(default='street',null=False)
    city = models.CharField(max_length=150, default='city',null=False)
    state = models.CharField(max_length=150,default='state', null=False)
    country = models.CharField(max_length=150, default='country', null=False)
    pincode = models.CharField(max_length=150,default='0', null=False)# Set null=False if user is mandatory
    order_date = models.DateTimeField(auto_now_add=True)
    payment_mode = models.CharField(max_length=150, null=False,default='mode')
    payment_id = models.CharField(max_length=250, null=True)
    
    orderstatuses = (
        ('Pending', 'Pending'),
        ('Out For Shipping', 'Out For Shipping'),
        ('Completed', 'Completed'),
    )
    
    
    message = models.TextField(null=True)
    tracking_no = models.CharField(max_length=150, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[  # Choices can be a tuple of tuples
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ], default='Pending')

    shipped_time = models.DateTimeField(null=True, blank=True)   
    out_for_delivery_time = models.DateTimeField(null=True, blank=True)
    delivered_time = models.DateTimeField(null=True, blank=True)
    courier_name = models.CharField(max_length=100, null=True, blank=True)

    
    

    def __str__(self):
        return '{}-{}'.format(self.id, self.tracking_no)


class Customize(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Set null=False if user is mandatory
    description = models.TextField()
    image = models.ImageField(upload_to='customize/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Custom Request by {self.user.username}"


class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    invoice_date = models.DateTimeField(auto_now_add=True)
    invoice_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Invoice #{self.invoice_number} for Order #{self.order.id}"


class Weight(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='product_weight')  # Use 'related_name'
    weight_in_grams = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.weight_in_grams}g"


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Set null=False if user is mandatory
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username} for {self.product.name}"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    message = models.TextField()

    def __str__(self):
        return self.name


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Set null=False if user is mandatory
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Set null=False if user is mandatory
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    payment_method = models.CharField(max_length=50, choices=[
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('PayPal', 'PayPal'),
        ('Cash on Delivery', 'Cash on Delivery'),
    ])
    payment_status = models.CharField(max_length=50, choices=[
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ], default='Pending')
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.payment_status}"

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User is required
    full_name = models.CharField(max_length=200, blank=True) 
    phone = models.CharField(max_length=15, blank=True, null=True)
    last_name = models.CharField(max_length=50,  blank=True)
    email = models.EmailField(default="example@email.com", blank=True)

    street_address = models.TextField(blank=True,null=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.IntegerField(default=0, blank=True,null=True)
    country = models.CharField(max_length=100, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.country}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length=150, default='fname', null=False)
    last_name = models.CharField(max_length=50,  blank=True) 
    phone = models.CharField(max_length=15,  blank=True, null=True)
    email = models.EmailField(default="example@email.com", blank=True)
    address = models.TextField(default='street',null=False)
    city = models.CharField(max_length=150, default='city',null=False)
    state = models.CharField(max_length=150,default='state', null=False)
    country = models.CharField(max_length=150, default='country', null=False)
    pincode = models.CharField(max_length=150,default='0', null=False)# Set null=False if user is mandatory
    
    def __str__(self):
        return self.user.username


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(null=False)

    def __str__(self):
        return '{} {}'.format(self.order.id,self.order.tracking_no)



class Report(models.Model):
    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"  # This will show "Reports" in admin panel

    def __str__(self):
        return "Generate Reports"
    
    
    