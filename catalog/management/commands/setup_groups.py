from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product
from blog.models import Post


class Command(BaseCommand):
    help = 'Создает группы и назначает права для HW-28'

    def handle(self, *args, **kwargs):
        # ==========================================
        # 1. Группа "Модератор продуктов"
        # ==========================================
        mod_group, created = Group.objects.get_or_create(name='Модератор продуктов')
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Группа "Модератор продуктов" создана'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Группа "Модератор продуктов" уже существует'))

        # Получаем права для Product
        content_type_product = ContentType.objects.get_for_model(Product)

        # Кастомное право can_unpublish_product
        perm_unpublish = Permission.objects.get(
            codename='can_unpublish_product',
            content_type=content_type_product
        )

        # Стандартное право на удаление продукта
        perm_delete = Permission.objects.get(
            codename='delete_product',
            content_type=content_type_product
        )

        # Назначаем права группе
        mod_group.permissions.add(perm_unpublish, perm_delete)
        self.stdout.write(
            self.style.SUCCESS('✅ Права назначены группе "Модератор продуктов": can_unpublish_product, delete_product'))

        # ==========================================
        # 2. Группа "Контент-менеджер" (доп. задание *)
        # ==========================================
        cm_group, created = Group.objects.get_or_create(name='Контент-менеджер')
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Группа "Контент-менеджер" создана'))
        else:
            self.stdout.write(self.style.WARNING('️ Группа "Контент-менеджер" уже существует'))

        # Получаем все права на модель Post
        content_type_post = ContentType.objects.get_for_model(Post)
        perms_post = Permission.objects.filter(content_type=content_type_post)

        # Назначаем все права на посты группе
        cm_group.permissions.set(perms_post)
        self.stdout.write(
            self.style.SUCCESS(f'✅ Права на блог назначены группе "Контент-менеджер" ({perms_post.count()} прав)'))

        self.stdout.write(self.style.SUCCESS('\n🎉 Настройка групп успешно завершена!'))
