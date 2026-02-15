# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.contrib import admin
from .models import VehicleCategory, Vehicle, VehicleImage

class VehicleImageInline(admin.TabularInline):
    """Allows adding gallery images directly when editing a vehicle"""
    model = VehicleImage
    extra = 3
    fields = ('image', 'caption', 'order')


@admin.register(VehicleCategory)
class VehicleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'vehicle_count')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}

    def vehicle_count(self, obj):
        return obj.vehicles.filter(is_active=True).count()

    vehicle_count.short_description = 'Active Vehicles'


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'passenger_capacity', 'pricing_display', 'is_active', 'image_preview')
    list_filter = ('category', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name', 'description')

    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'description', 'passenger_capacity')
        }),
        ('Pricing', {
            'fields': ('show_pricing', 'price', 'price_unit'),
            'description': 'If "Show pricing" is unchecked, a "Request Quote" button will appear instead.'
        }),
        ('Images', {
            'fields': ('featured_image',),
            'description': 'Upload the main photo here. Add gallery photos in the section below.'
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order'),
            'classes': ('collapse',)
        }),
    )

    inlines = [VehicleImageInline]

    def pricing_display(self, obj):
        if obj.show_pricing and obj.price:
            return f"${obj.price} {obj.price_unit}"
        return "Request Quote"

    pricing_display.short_description = 'Price'

    def image_preview(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                               obj.featured_image.url)
        return "No image"

    image_preview.short_description = 'Preview'


@admin.register(VehicleImage)
class VehicleImageAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'image_preview', 'caption', 'order')
    list_filter = ('vehicle__category',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "No image"

    image_preview.short_description = 'Preview'