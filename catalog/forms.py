from django import forms
from django.core.exceptions import ValidationError
from .models import Product

# Константа запрещённых слов (без пробелов на конце!)
FORBIDDEN_WORDS = [
    "казино", "криптовалюта", "крипта", "биржа",
    "дешево", "бесплатно", "обман", "полиция", "радар"
]


class ProductAddForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category']
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'price': 'Цена ($)',
            'image': 'Изображение',
            'category': 'Категория',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ЗАДАНИЕ 3: Стилизация через __init__ (строгое требование критериев)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

            # Добавляем плейсхолдеры тем полям, где их нет
            if field_name == 'name':
                field.widget.attrs['placeholder'] = 'Название товара'
            elif field_name == 'description':
                field.widget.attrs['placeholder'] = 'Описание'

    def _check_forbidden_words(self, value, field_name):
        """Вспомогательный метод для проверки запрещённых слов"""
        if value:
            value_lower = value.lower()
            for word in FORBIDDEN_WORDS:
                if word in value_lower:
                    raise ValidationError(
                        f"Поле '{field_name}' содержит запрещённое слово: '{word}'"
                    )
        return value

    def clean_name(self):
        """ЗАДАНИЕ 1: Валидация названия"""
        value = self.cleaned_data.get('name')
        return self._check_forbidden_words(value, 'Название')

    def clean_description(self):
        """ЗАДАНИЕ 1: Валидация описания"""
        value = self.cleaned_data.get('description')
        return self._check_forbidden_words(value, 'Описание')

    def clean_price(self):
        """ЗАДАНИЕ 2: Валидация цены (запрет отрицательных значений)"""
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise ValidationError("Цена продукта не может быть отрицательной. Проверьте вводимые данные.")
        return price

    def clean_image(self):
        """Допзадание: Валидация изображения"""
        image = self.cleaned_data.get('image')
        if image:
            # Проверка формата
            valid_formats = ['image/jpeg', 'image/png']
            if image.content_type not in valid_formats:
                raise ValidationError(
                    "Недопустимый формат изображения. Разрешены только JPEG и PNG."
                )

            # Проверка размера (5MB = 5 * 1024 * 1024 bytes)
            max_size = 5 * 1024 * 1024
            if image.size > max_size:
                raise ValidationError(
                    f"Размер файла превышает 5MB (текущий размер: {image.size / 1024 / 1024:.2f}MB)"
                )

        return image


class ContactForm(forms.Form):
    name = forms.CharField(label='Ваше имя', max_length=100)
    phone = forms.CharField(label='Телефон', max_length=20)
    message = forms.CharField(label='Сообщение', widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'
