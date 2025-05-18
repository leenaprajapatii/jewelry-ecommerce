from django.contrib import admin
from django.utils.html import format_html
from django.contrib import admin
from django.urls import path
from django.http import FileResponse
import io
from django.utils.timezone import now
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle




 # Ensure these models exist
  # Correct import

from .models import (
    Category,
    Subcategory,
    Product,
    Cart,
    Order,
    Customize,
    Invoice,
    Weight,
    Feedback,
    Wishlist,
    Payment,
    Coupon, Banner, ProductImage, Review, Size, UserProfile,Report,
)

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'discount', 'image_tag', 'active_status')
    list_filter = ('active_status',)
    search_fields = ('discount',)
    ordering = ('-id',)

    def image_tag(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "No Image"

    image_tag.short_description = 'Image Preview'
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'discount_percentage', 'min_order_amount', 'is_active', 'expiry_date')
    list_filter = ('is_active', 'expiry_date')
    search_fields = ('code',)
    ordering = ('-expiry_date',)
    actions = ['activate_coupons', 'deactivate_coupons']

    def activate_coupons(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected coupons have been activated.")

    def deactivate_coupons(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected coupons have been deactivated.")

    activate_coupons.short_description = "Activate selected coupons"
    deactivate_coupons.short_description = "Deactivate selected coupons"

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'image_tag')
    readonly_fields = ('image_tag',)
    prepopulated_fields = {'slug': ('name',)}  # Autofill slug field

    def image_tag(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "No Image"

    image_tag.short_description = 'Image Preview'


# Subcategory Admin
@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'description', 'display_image']
    search_fields = ['name', 'category__name']
    prepopulated_fields = {'slug': ('name',)}  # Autofill slug field
    list_filter = ['category']

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.image.url)
        return "No Image"

    display_image.short_description = "Image"


class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at','image')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')


class ProductImageInline(admin.TabularInline):  # 🔹 Inline for extra images
    model = ProductImage
    extra = 1  # Allows adding extra images while editing a product


# Product Admin

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'slug', 'price', 'category', 'stock', 'created_at', 'image_preview', 'hover_image_preview',
                    'material', 'purity', 'show_short_description']
    search_fields = ['name', 'sku', 'category__name', 'subcategory__name']
    list_filter = ['category', 'subcategory', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    inlines = [ProductImageInline]
    filter_horizontal = ('sizes',)
    readonly_fields = ('average_rating',) 

    def show_short_description(self, obj):
        return obj.generate_short_description()
    show_short_description.short_description = "Short Desc"

    def image_preview(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" style="height: 50px; width: auto;">')
        return "-"
    image_preview.short_description = "Image Preview"

    def hover_image_preview(self, obj):
        if obj.hover_image:
            return format_html(f'<img src="{obj.hover_image.url}" style="height: 50px; width: auto;">')
        return "-"
    hover_image_preview.short_description = "Hover Image Preview"



# Cart Admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'added_at']
    search_fields = ['user__username', 'product__name']
    list_filter = ['added_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'order_date', 'total_price', 'status']
    search_fields = ['user__username', 'status']
    list_filter = ['status', 'order_date']
    actions = ["mark_as_shipped", "mark_as_out_for_delivery", "mark_as_delivered"]

    def mark_as_shipped(self, request, queryset):
        queryset.update(status="Shipped", shipped_time=now())
    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def mark_as_out_for_delivery(self, request, queryset):
        queryset.update(status="Out For Delivery", out_for_delivery_time=now())
    mark_as_out_for_delivery.short_description = "Mark selected orders as Out For Delivery"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status="Completed", delivered_time=now())
    mark_as_delivered.short_description = "Mark selected orders as Delivered"



# # Customize Admin
# @admin.register(Customize)
# class CustomizeAdmin(admin.ModelAdmin):
#     list_display = ['user', 'description', 'created_at']
#     search_fields = ['user__username']
#     list_filter = ['created_at']


# Invoice Admin
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['order', 'invoice_number', 'invoice_date']
    search_fields = ['invoice_number', 'order__id']
    list_filter = ['invoice_date']


# Weight Admin
@admin.register(Weight)
class WeightAdmin(admin.ModelAdmin):
    list_display = ['product', 'weight_in_grams']
    search_fields = ['product__name']


# Feedback Admin
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'created_at']
    search_fields = ['user__username', 'product__name']
    list_filter = ['rating', 'created_at']


# Wishlist Admin
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    search_fields = ['user__username', 'product__name']
    list_filter = ['added_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'order', 'payment_method', 'payment_status', 'payment_date']
    search_fields = ['user__username', 'order__id']
    list_filter = ['payment_method', 'payment_status', 'payment_date']






class ReportAdmin(admin.ModelAdmin):
    change_list_template = "admin/reports.html"  # Ensure this template exists

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("report/generate/", self.admin_site.admin_view(self.generate_report), name="admin_generate_report"),
        ]
        return custom_urls + urls

    def generate_report(self, request):
        report_type = request.GET.get("report_type", "")
        start_date = request.GET.get("start_date", "")
        end_date = request.GET.get("end_date", "")

        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        elements = []

        # Title
        title = [[f"{report_type} Report"], [f"Date Range: {start_date} - {end_date}"]]
        title_table = Table(title, colWidths=[500])
        title_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]))
        elements.append(title_table)

        data = []

        # Fetch Data Based on Report Type
        if report_type == "Order":
            data = [["Order ID", "User", "Amount", "Status", "Date"]]
            orders = Order.objects.filter(created_at__range=[start_date, end_date])
            for order in orders:
                data.append([order.id, order.user.username, order.total_price, order.status, order.created_at])

        elif report_type == "Payment":
            data = [["Payment ID", "User", "Amount", "payment_status", "payment_date"]]
            payments = Payment.objects.filter(payment_date__range=[start_date, end_date])  
            for payment in payments:
                data.append([payment.id, payment.user.username, payment.amount, payment.payment_status, payment.payment_date])

        elif report_type == "Feedback":
            data = [["Feedback ID", "User", "Rating", "Comment", "Date"]]
            feedbacks = Feedback.objects.filter(created_at__range=[start_date, end_date])  # ✅ CORRECT FIELD
            for feedback in feedbacks:
                data.append([feedback.id, feedback.user.username, feedback.rating, feedback.comment or "No comment", feedback.created_at])  # ✅ FIXED FIELDS


        # Create Table with Styling
        table = Table(data, colWidths=[80, 120, 100, 100, 180])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)
        pdf.build(elements)

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"{report_type}_Report_{start_date}_{end_date}.pdf")


admin.site.register(Report, ReportAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Review, ReviewAdmin)

