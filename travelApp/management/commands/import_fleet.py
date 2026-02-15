"""
Django Management Command to Import Fleet Vehicles
Place this file in: travelApp/management/commands/import_fleet.py

Directory structure needed:
travelApp/
    management/
        __init__.py
        commands/
            __init__.py
            import_fleet.py  <- this file

Usage: python manage.py import_fleet
"""

from django.core.management.base import BaseCommand
from django.core.files import File
from travelApp.models import VehicleCategory, Vehicle, VehicleImage
from pathlib import Path
import os


class Command(BaseCommand):
    help = 'Import fleet vehicles from theme/fleet folder structure'

    def handle(self, *args, **kwargs):
        # Path to your fleet folder
        FLEET_BASE_PATH = Path('theme/Fleet')

        # Define categories and their order
        CATEGORIES = {
            'SUV & Sedan': {
                'order': 1,
                'description': 'Executive sedans and luxury SUVs perfect for business travel, airport transfers, and intimate occasions.'
            },
            'All Party Buses': {
                'order': 2,
                'description': 'Mobile nightclubs on wheels with sound systems, lighting, and luxurious interiors for unforgettable celebrations.'
            },
            'Stretch Limos': {
                'order': 3,
                'description': 'Classic stretch limousines for weddings, proms, and special events with elegant styling and premium amenities.'
            },
            'Charter buses': {
                'order': 4,
                'description': 'Comfortable charter buses and shuttles for group transportation, corporate events, and long-distance travel.'
            },
        }

        # Vehicle data structure based on your tree
        VEHICLES = {
            'SUV & Sedan': [
                {'name': 'Audi A8 L Sedan', 'capacity': 2, 'folder': 'Audi A8 L Sedan 2-pass 3 bags',
                 'description': 'Luxury German engineering meets executive comfort. Perfect for business travelers who demand the finest.'},
                {'name': 'BMW 750i Sedan', 'capacity': 3, 'folder': 'BMW 750i Sedan 2-3 pass 2 bags',
                 'description': 'Ultimate driving machine with sophisticated elegance. Ideal for airport transfers and business meetings.'},
                {'name': 'Chevrolet Suburban SUV Black', 'capacity': 7,
                 'folder': 'Chevrolet Subrban SUV Black 7 pass 4 bags',
                 'description': 'Spacious and versatile SUV perfect for families and group travel with ample luggage space.'},
                {'name': 'GMC Yukon SUV', 'capacity': 6, 'folder': 'GMC Yukon SUV 5-6 pass 2 bags',
                 'description': 'Premium American SUV combining comfort, power, and sophistication for any journey.'},
                {'name': 'Lincoln Town Car Sedan', 'capacity': 3, 'folder': 'Lincon Town Car (Sedan) 2-3 pass 2 bags',
                 'description': 'Classic American luxury sedan offering smooth rides and timeless elegance.'},
                {'name': 'Luxury Cadillac Escalade SUV', 'capacity': 5,
                 'folder': 'Luxury Cadillac Escalade SUV Black 5 pass 4 bags',
                 'description': 'The pinnacle of American luxury SUVs. Commanding presence with unmatched comfort and style.'},
                {'name': 'Mercedes S550 Sedan', 'capacity': 3, 'folder': 'Mercedes S550 (Sedan) 2-3 pass 2 bags',
                 'description': 'Flagship Mercedes sedan delivering ultimate luxury, technology, and prestige.'},
            ],
            'All Party Buses': [
                {'name': 'Amelia Party Bus', 'capacity': 35, 'folder': 'Amelia Party Bus for 35 pass',
                 'description': 'Spacious party bus with premium sound system and luxurious seating for medium-sized celebrations.'},
                {'name': 'Club On Wheels Party Bus', 'capacity': 45, 'folder': 'Club On Wheels party bus for 45 pass',
                 'description': 'Transform your event into a mobile nightclub with state-of-the-art lighting and sound.'},
                {'name': 'Club On Wheels Party Bus XL', 'capacity': 50,
                 'folder': 'Club on wheels party bus for 50 pass',
                 'description': 'Our largest Club On Wheels with capacity for 50 guests and premium entertainment features.'},
                {'name': 'Limo Luxury White Party Bus', 'capacity': 35,
                 'folder': 'Limo luxury white party bus for 35 pass',
                 'description': 'Stunning white exterior with limousine-style luxury interior perfect for weddings and upscale events.'},
                {'name': 'Limo Party Bus with Poles', 'capacity': 25,
                 'folder': 'Limo party bus for 25 pass with  poles',
                 'description': 'Intimate party atmosphere with dance poles and VIP seating for bachelorette parties and celebrations.'},
                {'name': 'Limo Party Bus', 'capacity': 35, 'folder': 'Limo Party bus for 35 pass',
                 'description': 'Classic party bus design with luxurious amenities and entertainment systems throughout.'},
                {'name': 'Limo Party Bus XL', 'capacity': 40, 'folder': 'Limo party bus for 40 pass',
                 'description': 'Extra-large capacity party bus perfect for big celebrations and group events.'},
                {'name': 'Limo Party Bus with 2 Poles', 'capacity': 28,
                 'folder': 'Limo Party bus with 2 ples for 28 pass',
                 'description': 'Dual dance poles create an energetic party atmosphere for unforgettable nights out.'},
                {'name': 'Mercedes Setra Party Bus', 'capacity': 60, 'folder': 'mERCEDES sETRA PARTY BUS FOR 60 PASS',
                 'description': 'Our largest party bus! Mercedes engineering meets party excellence for massive group celebrations.'},
                {'name': 'Mercedes Sprinter Limo Black', 'capacity': 14,
                 'folder': 'Mercedes Sprinter Limo Black 14 pass',
                 'description': 'Sleek black Mercedes Sprinter with limousine appointments and premium finishes.'},
                {'name': 'Mercedes Sprinter Limo White', 'capacity': 14,
                 'folder': 'Mercedes Sprinter Limo White 14 pass',
                 'description': 'Elegant white Mercedes Sprinter limo perfect for weddings and upscale celebrations.'},
                {'name': 'Party Bus Ford F-750 White', 'capacity': 50,
                 'folder': 'Party bus Ford F-750 white for 50 pass',
                 'description': 'Massive Ford F-750 chassis provides smooth ride for large party groups.'},
                {'name': 'Party Bus with Bathroom', 'capacity': 25,
                 'folder': 'Party bus with pole 20-25 pass with bathroom',
                 'description': 'Convenience meets party luxury with onboard bathroom facilities and dance pole.'},
                {'name': 'Queen Ann Party Bus', 'capacity': 20, 'folder': 'Quin Ann Party bus for 20 pass',
                 'description': 'Intimate party bus with royal treatment and upscale amenities for smaller groups.'},
                {'name': 'The Gem Club', 'capacity': 20, 'folder': 'The Gem on club for 15-20 pass',
                 'description': 'Hidden gem in our fleet offering boutique party experience with premium features.'},
                {'name': 'The Tiffany Party Bus', 'capacity': 26, 'folder': 'The Tiffany Party Bus for 26 pass',
                 'description': 'Luxury and elegance embodied in this sophisticated party bus with premium appointments.'},
                {'name': 'White Night Party Bus', 'capacity': 30, 'folder': 'White Night party bus for 30 pass',
                 'description': 'Pure white elegance with spectacular lighting creates magical nighttime atmosphere.'},
                {'name': 'White Tiffany Party Bus', 'capacity': 50, 'folder': 'White Tiffany party bus for 50 pass',
                 'description': 'Grand white party bus with Tiffany-inspired luxury for large upscale celebrations.'},
            ],
            'Stretch Limos': [
                {'name': 'Cadillac Escalade Stretch Black', 'capacity': 20,
                 'folder': 'Cadillac Escalade Stretch black for 18-20 pass',
                 'description': 'Iconic Escalade stretched to perfection with luxury seating and premium entertainment.'},
                {'name': 'Cadillac Escalade Stretch with Jet Doors', 'capacity': 20,
                 'folder': 'Cadillac Escalade Stretch jet doors for 18-20 pass',
                 'description': 'Dramatic jet-door entry makes a statement. Perfect for proms and red carpet arrivals.'},
                {'name': 'Cadillac Escalade Super Stretch', 'capacity': 20,
                 'folder': 'Cadillac Escalade super stretch for 20 pass',
                 'description': 'Extended wheelbase Escalade offering maximum space and luxury for your special event.'},
                {'name': 'Chrysler 300 Stretch Black', 'capacity': 10,
                 'folder': 'Chrysler 300 stretch black for 8-10 pass',
                 'description': 'Sleek black stretch limo with modern styling perfect for intimate celebrations.'},
                {'name': 'Chrysler 300 Stretch White', 'capacity': 10,
                 'folder': 'Chrysler 300 Stretch white for 8-10 pass',
                 'description': 'Classic white stretch limo ideal for weddings, proms, and elegant affairs.'},
                {'name': 'Chrysler 300 White with Jet Doors', 'capacity': 12,
                 'folder': 'Chrysler 300 white jet doors for 10-12 pass',
                 'description': 'White elegance meets dramatic jet-door styling for unforgettable entrances.'},
                {'name': 'Hummer H2 Stretch White', 'capacity': 20, 'folder': 'Hummer H2 Stretch white for 20 pass',
                 'description': 'Commanding white Hummer stretch offers bold style and spacious luxury interior.'},
                {'name': 'Hummer Stretch Pink', 'capacity': 20, 'folder': 'Hummer Stretch pink for 20 pass',
                 'description': 'Fun and fabulous pink Hummer perfect for bachelorette parties and girls nights out.'},
                {'name': 'Lincoln MKT Stretch Limo', 'capacity': 10,
                 'folder': 'Lincoln MKT stretch limo white & black 8-10 pass',
                 'description': 'Modern Lincoln design with two-tone styling and contemporary luxury features.'},
                {'name': 'Luxury Lincoln Navigator Stretch', 'capacity': 20,
                 'folder': 'Luxury Lincoln Navegator Stretch white for 20 pass',
                 'description': 'Premium Navigator stretch combining American luxury with spacious comfort.'},
            ],
            'Charter buses': [
                {'name': '30 Passenger Charter Bus', 'capacity': 30, 'folder': '30 pas bus charter',
                 'description': 'Comfortable mid-size charter bus perfect for corporate events and group outings.'},
                {'name': '45 Passenger Charter Bus', 'capacity': 45, 'folder': '40-45 pass charter',
                 'description': 'Large capacity charter with comfortable seating for extended group travel.'},
                {'name': 'Black Executive Mercedes Sprinter', 'capacity': 14,
                 'folder': 'Black Executive Mercedes sprinter for 14 pass',
                 'description': 'Executive-class Mercedes Sprinter with premium seating and business amenities.'},
                {'name': 'Coach Bus', 'capacity': 55, 'folder': 'Coach Bus for 55 pass',
                 'description': 'Full-size luxury coach bus perfect for long-distance travel and large groups.'},
                {'name': 'Ford F550 Shuttle Bus', 'capacity': 25, 'folder': 'Ford F550 Shuttle Bus for 25 pass',
                 'description': 'Reliable shuttle service for airport transfers and local group transportation.'},
                {'name': 'Ford Rear-Window Shuttle', 'capacity': 50, 'folder': 'Ford REAR-WINDOW Shuttle for 50 pass',
                 'description': 'Large capacity shuttle with panoramic views for sightseeing and group tours.'},
                {'name': 'Freightliner Shuttle Bus', 'capacity': 40, 'folder': 'Freightliner Shuttle bujs for 40 pass',
                 'description': 'Heavy-duty Freightliner chassis ensures smooth ride for large group transportation.'},
                {'name': 'Mercedes Sprinter Corporate Van', 'capacity': 14,
                 'folder': 'Mercedes Sprinter Corporate Van for 14 pass',
                 'description': 'Professional corporate transport with Wi-Fi and business-class seating.'},
                {'name': 'Mercedes Sprinter Executive Van', 'capacity': 14,
                 'folder': 'Mercedes Sprinter Executive Van for 14 pass',
                 'description': 'Top-tier Mercedes Sprinter with luxury captain chairs and premium amenities.'},
                {'name': 'Mercedes Sprinter Shuttle', 'capacity': 14,
                 'folder': 'Mercedes Sprinter Shuttel for 12-14 pass',
                 'description': 'Versatile Mercedes shuttle perfect for airport runs and local group transport.'},
                {'name': 'Mini Shuttle Bus 26', 'capacity': 26, 'folder': 'Mini Shuttle Bus for 26 pass',
                 'description': 'Compact shuttle ideal for mid-size groups and local transportation needs.'},
                {'name': 'Mini Shuttle Bus 36', 'capacity': 36, 'folder': 'Mini Shuttle Bus for 36 pass',
                 'description': 'Larger mini shuttle offering comfortable transport for medium-sized groups.'},
            ],
        }

        self.stdout.write(self.style.SUCCESS('Starting fleet import...'))

        # Create categories
        for cat_name, cat_data in CATEGORIES.items():
            category, created = VehicleCategory.objects.get_or_create(
                name=cat_name,
                defaults={
                    'slug': cat_name.lower().replace(' ', '-').replace('&', 'and'),
                    'description': cat_data['description'],
                    'order': cat_data['order']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created category: {cat_name}'))
            else:
                self.stdout.write(f'  Category already exists: {cat_name}')

        # Import vehicles
        total_vehicles = 0
        total_images = 0

        for cat_name, vehicles in VEHICLES.items():
            category = VehicleCategory.objects.get(name=cat_name)

            for idx, vehicle_data in enumerate(vehicles, 1):
                vehicle, created = Vehicle.objects.get_or_create(
                    category=category,
                    name=vehicle_data['name'],
                    defaults={
                        'description': vehicle_data['description'],
                        'passenger_capacity': vehicle_data['capacity'],
                        'show_pricing': False,  # Set to True if you want to show prices
                        'is_active': True,
                        'order': idx,
                    }
                )

                if created:
                    total_vehicles += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created vehicle: {vehicle_data["name"]}'))

                    # Import images from folder
                    vehicle_folder = FLEET_BASE_PATH / cat_name / vehicle_data['folder']

                    if vehicle_folder.exists():
                        image_files = []
                        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
                            image_files.extend(vehicle_folder.glob(ext))

                        if image_files:
                            # First image becomes featured image
                            first_image = sorted(image_files)[0]
                            with open(first_image, 'rb') as f:
                                vehicle.featured_image.save(
                                    first_image.name,
                                    File(f),
                                    save=True
                                )
                            self.stdout.write(f'    → Featured image: {first_image.name}')
                            total_images += 1

                            # Rest become gallery images
                            for img_path in sorted(image_files)[1:]:
                                with open(img_path, 'rb') as f:
                                    gallery_img = VehicleImage.objects.create(
                                        vehicle=vehicle,
                                        order=len(image_files)
                                    )
                                    gallery_img.image.save(
                                        img_path.name,
                                        File(f),
                                        save=True
                                    )
                                total_images += 1

                            self.stdout.write(f'    → Added {len(image_files) - 1} gallery images')
                        else:
                            self.stdout.write(self.style.WARNING(f'    ⚠ No images found in {vehicle_folder}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'    ⚠ Folder not found: {vehicle_folder}'))
                else:
                    self.stdout.write(f'  Vehicle already exists: {vehicle_data["name"]}')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Import complete!'))
        self.stdout.write(self.style.SUCCESS(f'   Total vehicles created: {total_vehicles}'))
        self.stdout.write(self.style.SUCCESS(f'   Total images imported: {total_images}'))