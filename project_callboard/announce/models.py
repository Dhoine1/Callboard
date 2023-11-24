from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor.fields import RichTextField


# Create your models here.
class Category(models.Model):
    type = models.CharField(max_length=32, verbose_name='Название категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.type}'


class Note(models.Model):
    header = models.CharField(max_length=128, verbose_name='Заголовок объявления')
    text = RichTextField()
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор объявления')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория объявления')

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'

    def __str__(self):
        time = self.create_date.strftime("%Y-%m-%d %H:%M:%S")
        return f'{self.header} - Автор: {self.author} - Создан: ({time})'

    def get_absolute_url(self):
        return reverse('Note', args=[str(self.id)])


class Comments(models.Model):
    text = models.CharField(max_length=1024, verbose_name='Текст отклика')
    author_of_call = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор отклика')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    to_note = models.ForeignKey(Note, on_delete=models.CASCADE, verbose_name='К статье')
    status = models.BooleanField(default=False, verbose_name='Статус комментария')

    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'

    def __str__(self):
        time = self.date.strftime("%Y-%m-%d %H:%M:%S")
        return f'({time}) {self.text[:128]} - Автор: {self.author_of_call}'