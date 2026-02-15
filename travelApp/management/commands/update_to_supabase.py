# core/management/commands/update_to_supabase.py
from django.core.management.base import BaseCommand
from supabase import create_client
from django.conf import settings
from travelApp.models import Vehicle, VehicleImage


class Command(BaseCommand):
    help = 'Update existing vehicles to use Supabase images'

    def handle(self, *args, **kwargs):
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

        self.stdout.write(self.style.SUCCESS('\n🔄 Updating vehicles to use Supabase images...\n'))

        # Mapping: Database category name → Supabase folder name
        category_to_folder = {
            'SUV & Sedan': 'SUV & Sedan',
            'All Party Buses': 'All Party Buses',
            'Stretch Limos': 'Stretch Limos',
            'Charter buses': 'Charter buses',
        }

        updated_count = 0
        failed_count = 0

        vehicles = Vehicle.objects.all().order_by('category__name', 'name')
        total = vehicles.count()

        self.stdout.write(f'Found {total} vehicles to update\n')

        for idx, vehicle in enumerate(vehicles, 1):
            self.stdout.write(f'[{idx}/{total}] {vehicle.name}')

            category_name = vehicle.category.name
            supabase_folder = category_to_folder.get(category_name)

            if not supabase_folder:
                self.stdout.write(f'  ⚠️  Unknown category: {category_name}\n')
                failed_count += 1
                continue

            try:
                # List all vehicle folders in this category
                vehicle_folders = client.storage.from_('car_images').list(supabase_folder)

                if not vehicle_folders:
                    self.stdout.write(f'  ⚠️  No folders in {supabase_folder}\n')
                    failed_count += 1
                    continue

                # Try to find matching folder
                matched_folder = None

                # Strategy 1: Exact name match (case-insensitive)
                vehicle_name_lower = vehicle.name.lower()
                for folder in vehicle_folders:
                    folder_name = folder.get('name', '')
                    if vehicle_name_lower == folder_name.lower().split(' for ')[0].strip():
                        matched_folder = folder_name
                        break

                # Strategy 2: Partial match
                if not matched_folder:
                    for folder in vehicle_folders:
                        folder_name = folder.get('name', '')
                        folder_clean = folder_name.lower().split(' for ')[0].strip()

                        if vehicle_name_lower in folder_clean or folder_clean in vehicle_name_lower:
                            matched_folder = folder_name
                            break

                # Strategy 3: Word overlap
                if not matched_folder:
                    vehicle_words = set(vehicle_name_lower.split())
                    best_match = None
                    best_score = 0

                    for folder in vehicle_folders:
                        folder_name = folder.get('name', '')
                        folder_words = set(folder_name.lower().split())

                        overlap = len(vehicle_words & folder_words)
                        if overlap > best_score:
                            best_score = overlap
                            best_match = folder_name

                    if best_score >= 2:  # At least 2 words match
                        matched_folder = best_match

                if not matched_folder:
                    self.stdout.write(f'  ⚠️  No matching folder found')
                    self.stdout.write(f'     Available folders:')
                    for folder in vehicle_folders[:3]:  # Show first 3
                        self.stdout.write(f'       - {folder.get("name")}')
                    self.stdout.write('')
                    failed_count += 1
                    continue

                # Get images from matched folder
                vehicle_path = f"{supabase_folder}/{matched_folder}"
                images = client.storage.from_('car_images').list(vehicle_path)

                image_files = [
                    img for img in images
                    if img.get('name', '').lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
                       and img.get('id')
                ]

                if not image_files:
                    self.stdout.write(f'  ⚠️  No images in: {matched_folder}\n')
                    failed_count += 1
                    continue

                # Update featured image
                first_image = image_files[0]['name']
                new_path = f"{supabase_folder}/{matched_folder}/{first_image}"
                vehicle.featured_image = new_path
                vehicle.save()

                # Clear old gallery images and add new ones
                vehicle.gallery_images.all().delete()

                for img_idx, img in enumerate(image_files):
                    gallery_path = f"{supabase_folder}/{matched_folder}/{img['name']}"
                    VehicleImage.objects.create(
                        vehicle=vehicle,
                        image=gallery_path,
                        caption=f"{vehicle.name} - Photo {img_idx + 1}",
                        order=img_idx
                    )

                self.stdout.write(f'  ✓ Matched to: {matched_folder}')
                self.stdout.write(f'  ✓ {len(image_files)} images\n')
                updated_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error: {str(e)}\n'))
                import traceback
                traceback.print_exc()
                failed_count += 1

        # Summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ UPDATE COMPLETE!'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'\n📊 Results:')
        self.stdout.write(f'   ✓ Updated: {updated_count} vehicles')
        self.stdout.write(f'   ✗ Failed: {failed_count} vehicles')

        if failed_count > 0:
            self.stdout.write(f'\n⚠️  Some vehicles could not be matched.')
            self.stdout.write(f'   These may need manual review in Django admin.')

        self.stdout.write(f'\n✅ Check your website - images should now load from Supabase!\n')