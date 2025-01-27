import os
from django.core.files import File
from airbnb.models import HouseListing, ListingImage, PropertyType, RoomType, Amenity, AUTH_USER_MODEL

# Assuming you have already created the PropertyType, RoomType, Amenity, and User instances
property_type = PropertyType.objects.get(id=1)  # Replace with actual ID
room_type = RoomType.objects.get(id=1)  # Replace with actual ID
amenities = Amenity.objects.all()[:3]  # Replace with actual IDs or logic
host = AUTH_USER_MODEL.objects.get(id=1)  # Replace with actual ID

# Directory containing house images
image_directory = r'C:\Users\nahom\OneDrive\Pictures\Houses'

# List of image filenames in the directory
image_files = [f for f in os.listdir(image_directory) if os.path.isfile(os.path.join(image_directory, f))]

# Create 6 listings
for i in range(1, 7):
    listing = HouseListing(
        title=f'House Listing {i}',
        serial_number=f'SN00{i}',
        description=f'This is a beautiful house located in a serene environment. Listing {i}',
        property_type=property_type,
        room_type=room_type,
        address=f'{i} Main St',
        city='New York',
        state='NY',
        country='USA',
        latitude=40.7128 + (i * 0.01),
        longitude=-74.0060 + (i * 0.01),
        price_per_month=0.1,
        price_per_night=0.01,
        cleaning_fee=10.00,
        security_deposit=100.00,
        extra_guest_fee=5.00,
        minimum_stay=2,
        maximum_stay=30,
        cancellation_policy='Flexible',
        house_rules='No smoking, no pets.',
        host=host,
        is_wheelchair_accessible=(i % 2 == 0),
        has_step_free_access=(i % 2 == 0),
        accessible_bathroom=(i % 2 == 0),
    )
    listing.save()

    # Add amenities to the listing
    listing.amenities.set(amenities)

    # Add images to the listing
    if i <= len(image_files):
        image_path = os.path.join(image_directory, image_files[i-1])
        with open(image_path, 'rb') as f:
            listing_image = ListingImage(listing=listing)
            listing_image.image.save(image_files[i-1], File(f))
            listing_image.save()

    print(f'Created listing {i}')

print('All listings created successfully!')