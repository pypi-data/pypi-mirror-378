from django.core.management.base import BaseCommand
from django_autocomplete.core import generate_class_index

class Command(BaseCommand):
    help = 'Generate class index for auto-import functionality'

    def handle(self, *args, **options):
        self.stdout.write('Generating class index...')
        class_index = generate_class_index()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated index with {len(class_index)} classes')
        )