# fleet/management/commands/sync_supabase.py
from django.core.management.base import BaseCommand
from supabase import create_client
from django.conf import settings
from travelApp.models import VehicleCategory, Vehicle, VehicleImage


class Command(BaseCommand):
    help = 'Sync vehicle images with Supabase storage structure'

    def handle(self, *args, **kwargs):
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

        category_mapping = {
            'All Party Buses': 'all-party-buses',
            'Charter buses': 'charter-buses',
            'Stretch Limos': 'stretch-limos',
            'SUV & Sedan': 'suv-and-sedan',  # ← NOW MATCHES YOUR DB
        }

        self.stdout.write(self.style.SUCCESS('\n🚀 Starting Supabase sync...\n'))

        total_created = 0
        total_updated = 0

        for supabase_folder, category_slug in category_mapping.items():
            self.stdout.write('=' * 70)
            self.stdout.write(self.style.SUCCESS(f'📁 {supabase_folder}'))
            self.stdout.write('=' * 70)

            # Get or create category
            category, created = VehicleCategory.objects.get_or_create(
                slug=category_slug,
                defaults={
                    'name': supabase_folder,
                    'description': f'Fleet of {supabase_folder}',
                    'order': list(category_mapping.keys()).index(supabase_folder)
                }
            )

            try:
                # List all vehicle folders in this category
                items = client.storage.from_('car_images').list(supabase_folder)

                if not items:
                    self.stdout.write(self.style.WARNING(f'  ⚠️  No items found\n'))
                    continue

                self.stdout.write(f'Found {len(items)} potential vehicles\n')

                for item in items:
                    vehicle_folder_name = item.get('name')

                    if not vehicle_folder_name:
                        continue

                    vehicle_path = f"{supabase_folder}/{vehicle_folder_name}"

                    try:
                        # List images in vehicle folder
                        images = client.storage.from_('car_images').list(vehicle_path)

                        # Filter for actual image files
                        image_files = [
                            img for img in images
                            if img.get('name', '').lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
                               and img.get('id')  # Has an ID means it's a file, not a folder
                        ]

                        if not image_files:
                            self.stdout.write(f'  ⚠️  No images: {vehicle_folder_name}')
                            continue

                        # Extract clean vehicle name
                        clean_name = vehicle_folder_name
                        if ' for ' in clean_name and ' pass' in clean_name:
                            clean_name = clean_name.split(' for ')[0].strip()

                        # Extract passenger capacity
                        passenger_capacity = 10  # default
                        if ' for ' in vehicle_folder_name and ' pass' in vehicle_folder_name:
                            try:
                                capacity_str = vehicle_folder_name.split(' for ')[1].split(' pass')[0].strip()
                                # Handle ranges like "18-20" or "5-6"
                                if '-' in capacity_str:
                                    capacity_str = capacity_str.split('-')[-1]  # Take higher number
                                passenger_capacity = int(capacity_str)
                            except:
                                pass

                        # First image as featured
                        first_image = image_files[0]['name']
                        featured_path = f"{supabase_folder}/{vehicle_folder_name}/{first_image}"

                        # Create or update vehicle
                        vehicle, v_created = Vehicle.objects.get_or_create(
                            name=clean_name,
                            category=category,
                            defaults={
                                'description': f'{clean_name} - {category.name}',
                                'passenger_capacity': passenger_capacity,
                                'featured_image': featured_path,
                                'show_pricing': False,
                                'is_active': True,
                                'order': 0,
                            }
                        )

                        if not v_created:
                            vehicle.featured_image = featured_path
                            vehicle.passenger_capacity = passenger_capacity
                            vehicle.save()
                            total_updated += 1
                        else:
                            total_created += 1

                        # Clear old gallery images
                        vehicle.gallery_images.all().delete()

                        # Add all images to gallery
                        for idx, img in enumerate(image_files):
                            gallery_path = f"{supabase_folder}/{vehicle_folder_name}/{img['name']}"
                            VehicleImage.objects.create(
                                vehicle=vehicle,
                                image=gallery_path,
                                caption=f"{clean_name} - Photo {idx + 1}",
                                order=idx
                            )

                        # Output
                        icon = '✨' if v_created else '🔄'
                        action = 'Created' if v_created else 'Updated'
                        self.stdout.write(
                            f'  {icon} {action}: {clean_name} '
                            f'({passenger_capacity} pass, {len(image_files)} images)'
                        )

                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f'  ⚠️  Error with {vehicle_folder_name}: {str(e)}'
                        ))
                        continue

                self.stdout.write('')  # Empty line

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}\n'))

        # Final summary
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ SYNC COMPLETE!'))
        self.stdout.write('=' * 70)

        total_categories = VehicleCategory.objects.count()
        total_vehicles = Vehicle.objects.count()
        total_images = VehicleImage.objects.count()

        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'   Categories: {total_categories}')
        self.stdout.write(f'   Vehicles: {total_vehicles} ({total_created} created, {total_updated} updated)')
        self.stdout.write(f'   Gallery Images: {total_images}')
        self.stdout.write(f'\n✅ Go to Django admin at /admin/fleet/vehicle/ to review!\n')