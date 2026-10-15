from django.core.management.base import BaseCommand
from django.core.management import call_command
from catalog.models import Category, Product


class Command(BaseCommand):
    help = 'Загружает тестовые данные из фикстур, предварительно очищая базу'

    def handle(self, *args, **kwargs):
        # Удаляем все существующие данные
        self.stdout.write('🗑️  Удаляем старые данные...')
        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✅ Старые данные удалены'))

        # Загружаем фикстуры
        self.stdout.write('📦 Загружаем фикстуры...')
        call_command('loaddata', 'initial_data.json')
        self.stdout.write(self.style.SUCCESS('✅ Тестовые данные успешно загружены!'))

        # Показываем статистику
        categories_count = Category.objects.count()
        products_count = Product.objects.count()
        self.stdout.write(f'📊 Загружено: {categories_count} категорий, {products_count} продуктов')
