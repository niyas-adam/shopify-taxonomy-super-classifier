from django.core.management.base import BaseCommand
from classification.models import TaxonomyCategory
from .seed_taxonomy_data import TAXONOMY_DATA


class Command(BaseCommand):
    help = 'Seed the Shopify taxonomy with standard product categories'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing taxonomy before seeding')
        parser.add_argument('--count-only', action='store_true', help='Only print count')

    def handle(self, *args, **options):
        if options['count_only']:
            count = TaxonomyCategory.objects.count()
            self.stdout.write(f'Current taxonomy categories: {count}')
            return
        if options['clear']:
            TaxonomyCategory.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared all taxonomy categories'))
        id_to_obj = {}
        created = 0
        skipped = 0
        for entry in TAXONOMY_DATA:
            shopify_id, name, full_path, parent_id, level, keywords, hint, top_cat = entry
            if TaxonomyCategory.objects.filter(shopify_id=shopify_id).exists():
                skipped += 1
                continue
            cat = TaxonomyCategory.objects.create(
                shopify_id=shopify_id, name=name, full_path=full_path,
                level=level, keywords=keywords, product_type_hint=hint,
                top_level_category=top_cat,
            )
            id_to_obj[shopify_id] = cat
            created += 1
        for entry in TAXONOMY_DATA:
            shopify_id, name, full_path, parent_id, level, keywords, hint, top_cat = entry
            if parent_id and parent_id in id_to_obj:
                cat = id_to_obj.get(shopify_id)
                if cat:
                    cat.parent = id_to_obj[parent_id]
                    cat.save(update_fields=['parent'])
        total = TaxonomyCategory.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Seeded taxonomy: {created} created, {skipped} skipped, {total} total'))