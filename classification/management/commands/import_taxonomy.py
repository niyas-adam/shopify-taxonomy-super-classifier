from django.db import models
from django.core.management.base import BaseCommand
import json
import os
from classification.models import TaxonomyCategory


SHOPIFY_TAXONOMY = [
    {'shopify_id': 'home_garden', 'name': 'Home & Garden', 'path': 'Home & Garden', 'level': 0},
    {'shopify_id': 'furniture', 'name': 'Furniture', 'path': 'Home & Garden > Furniture', 'level': 1, 'parent': 'home_garden'},
    {'shopify_id': 'living_room', 'name': 'Living Room Furniture', 'path': 'Home & Garden > Furniture > Living Room Furniture', 'level': 2, 'parent': 'furniture'},
    {'shopify_id': 'sofas', 'name': 'Sofas', 'path': 'Home & Garden > Furniture > Living Room Furniture > Sofas', 'level': 3, 'parent': 'living_room', 'keywords': 'sofa couch settee loveseat sectional'},
    {'shopify_id': 'coffee_tables', 'name': 'Coffee Tables', 'path': 'Home & Garden > Furniture > Living Room Furniture > Coffee Tables', 'level': 3, 'parent': 'living_room', 'keywords': 'coffee table cocktail table center table'},
    {'shopify_id': 'bedroom', 'name': 'Bedroom Furniture', 'path': 'Home & Garden > Furniture > Bedroom Furniture', 'level': 2, 'parent': 'furniture'},
    {'shopify_id': 'beds', 'name': 'Beds & Bed Frames', 'path': 'Home & Garden > Furniture > Bedroom Furniture > Beds & Bed Frames', 'level': 3, 'parent': 'bedroom', 'keywords': 'bed frame bedframe platform bed headboard'},
    {'shopify_id': 'dressers', 'name': 'Dressers', 'path': 'Home & Garden > Furniture > Bedroom Furniture > Dressers', 'level': 3, 'parent': 'bedroom', 'keywords': 'dresser chest drawers wardrobe'},
    {'shopify_id': 'dining', 'name': 'Dining Furniture', 'path': 'Home & Garden > Furniture > Dining Furniture', 'level': 2, 'parent': 'furniture'},
    {'shopify_id': 'dining_tables', 'name': 'Dining Tables', 'path': 'Home & Garden > Furniture > Dining Furniture > Dining Tables', 'level': 3, 'parent': 'dining', 'keywords': 'dining table kitchen table eating table'},
    {'shopify_id': 'dining_chairs', 'name': 'Dining Chairs', 'path': 'Home & Garden > Furniture > Dining Furniture > Dining Chairs', 'level': 3, 'parent': 'dining', 'keywords': 'dining chair kitchen chair'},
    {'shopify_id': 'office', 'name': 'Office Furniture', 'path': 'Home & Garden > Furniture > Office Furniture', 'level': 2, 'parent': 'furniture'},
    {'shopify_id': 'office_chairs', 'name': 'Office Chairs', 'path': 'Home & Garden > Furniture > Office Furniture > Office Chairs', 'level': 3, 'parent': 'office', 'keywords': 'office chair desk chair task chair ergonomic chair'},
    {'shopify_id': 'desks', 'name': 'Desks', 'path': 'Home & Garden > Furniture > Office Furniture > Desks', 'level': 3, 'parent': 'office', 'keywords': 'desk writing desk computer desk work desk standing desk'},
    {'shopify_id': 'lighting', 'name': 'Lighting', 'path': 'Home & Garden > Lighting', 'level': 1, 'parent': 'home_garden'},
    {'shopify_id': 'ceiling_lights', 'name': 'Ceiling Lights', 'path': 'Home & Garden > Lighting > Ceiling Lights', 'level': 2, 'parent': 'lighting', 'keywords': 'ceiling light chandelier pendant flush mount'},
    {'shopify_id': 'table_lamps', 'name': 'Table Lamps', 'path': 'Home & Garden > Lighting > Table Lamps', 'level': 2, 'parent': 'lighting', 'keywords': 'table lamp desk lamp reading lamp'},
    {'shopify_id': 'floor_lamps', 'name': 'Floor Lamps', 'path': 'Home & Garden > Lighting > Floor Lamps', 'level': 2, 'parent': 'lighting', 'keywords': 'floor lamp standing lamp torchiere'},
    {'shopify_id': 'decor', 'name': 'Home Decor', 'path': 'Home & Garden > Decor', 'level': 1, 'parent': 'home_garden'},
    {'shopify_id': 'wall_art', 'name': 'Wall Art', 'path': 'Home & Garden > Decor > Wall Art', 'level': 2, 'parent': 'decor', 'keywords': 'wall art painting poster print canvas'},
    {'shopify_id': 'mirrors', 'name': 'Mirrors', 'path': 'Home & Garden > Decor > Mirrors', 'level': 2, 'parent': 'decor', 'keywords': 'mirror wall mirror standing mirror'},
    {'shopify_id': 'pillows', 'name': 'Throw Pillows', 'path': 'Home & Garden > Decor > Throw Pillows', 'level': 2, 'parent': 'decor', 'keywords': 'throw pillow cushion pillow decorative pillow'},
    {'shopify_id': 'rugs', 'name': 'Rugs & Carpets', 'path': 'Home & Garden > Decor > Rugs & Carpets', 'level': 2, 'parent': 'decor', 'keywords': 'rug carpet area rug runner mat'},
    {'shopify_id': 'storage', 'name': 'Storage & Organization', 'path': 'Home & Garden > Storage & Organization', 'level': 1, 'parent': 'home_garden'},
    {'shopify_id': 'shelving', 'name': 'Shelving & Storage', 'path': 'Home & Garden > Storage & Organization > Shelving & Storage', 'level': 2, 'parent': 'storage', 'keywords': 'shelf shelving bookcase storage rack'},
    {'shopify_id': 'outdoor', 'name': 'Outdoor & Garden', 'path': 'Home & Garden > Outdoor & Garden', 'level': 1, 'parent': 'home_garden'},
    {'shopify_id': 'patio_furniture', 'name': 'Patio Furniture', 'path': 'Home & Garden > Outdoor & Garden > Patio Furniture', 'level': 2, 'parent': 'outdoor', 'keywords': 'patio outdoor garden deck lawn furniture'},
    {'shopify_id': 'planters', 'name': 'Planters & Garden Decor', 'path': 'Home & Garden > Outdoor & Garden > Planters & Garden Decor', 'level': 2, 'parent': 'outdoor', 'keywords': 'planter flower pot garden planter planter box'},
    {'shopify_id': 'kitchen', 'name': 'Kitchen & Dining', 'path': 'Home & Garden > Kitchen & Dining', 'level': 1, 'parent': 'home_garden'},
    {'shopify_id': 'cookware', 'name': 'Cookware', 'path': 'Home & Garden > Kitchen & Dining > Cookware', 'level': 2, 'parent': 'kitchen', 'keywords': 'cookware pot pan skillet griddle'},
    {'shopify_id': 'dinnerware', 'name': 'Dinnerware', 'path': 'Home & Garden > Kitchen & Dining > Dinnerware', 'level': 2, 'parent': 'kitchen', 'keywords': 'dinnerware plates bowls dishes'},
    {'shopify_id': 'bathroom', 'name': 'Bathroom', 'path': 'Home & Garden > Bathroom', 'level': 1, 'parent': 'home_garden'},
    {'shopify_id': 'bathroom_storage', 'name': 'Bathroom Storage', 'path': 'Home & Garden > Bathroom > Bathroom Storage', 'level': 2, 'parent': 'bathroom', 'keywords': 'bathroom storage cabinet shelf'},
]


class Command(BaseCommand):
    help = 'Import Shopify taxonomy categories'

    def handle(self, *args, **options):
        self.stdout.write('Importing Shopify taxonomy...')
        created = 0
        updated = 0
        nodes_map = {}
        for item in SHOPIFY_TAXONOMY:
            parent = None
            if 'parent' in item and item['parent'] in nodes_map:
                parent = nodes_map[item['parent']]
            node, is_new = TaxonomyCategory.objects.update_or_create(
                shopify_id=item['shopify_id'],
                defaults={
                    'name': item['name'],
                    'full_path': item['path'],
                    'level': item['level'],
                    'parent': parent,
                    'keywords': item.get('keywords', ''),
                }
            )
            nodes_map[item['shopify_id']] = node
            if is_new:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Done: {created} created, {updated} updated'))