from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'preview',]
        labels = {
            'title': 'Заголовок',
            'content': 'Содержимое',
            'preview': 'Превью',
            'is_published': 'Опубликовано',
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Применяем стили Bootstrap
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control'

            # Добавляем плейсхолдеры для текстовых полей
            if field_name == 'title':
                field.widget.attrs['placeholder'] = 'Например: Как мы создавали Skystore'
            elif field_name == 'content':
                field.widget.attrs['placeholder'] = 'Текст статьи...'
