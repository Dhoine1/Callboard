from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Note, Comments
from .forms import NoteForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.core.mail import EmailMultiAlternatives


class NoteList(ListView):
    model = Note
    ordering = ['-create_date']
    template_name = 'index.html'
    context_object_name = 'notes'
    paginate_by = 20


# вьюшка объявления с полем для отклика
def notedetail(request, pk, **kwargs):
    note_now = Note.objects.filter(pk__exact=pk)

    for i in note_now:
        comments_to_note = Comments.objects.filter(to_note=i)
        note_id = i.pk
        header = i.header
        create_date = i.create_date
        author = i.author
        category = i.category
        text = i.text

        # если написали отклик
        if request.method == "POST":
            comment = Comments()
            comment.text = request.POST.get("text")
            comment.author_of_call = request.user
            comment.to_note = i
            # отправка автору сообщения о новом отклике
            email = comment.to_note.author.email
            subject = 'Новый отклик на ваше объявление'
            text_content = (
                f'Объявление: {comment.to_note.header}\n'
                f'Отклик: {comment.text}\n\n'
            )
            html_content = (
                f'Объявление: {comment.to_note.header}<br>'
                f'Отклик: {comment.text}<br><br>'
            )
            msg = EmailMultiAlternatives(subject, text_content, None, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            comment.save()
            return render(request, 'success.html')

    return render(request, 'note.html', {'header': header,
                                         'note_id': note_id,
                                         'creation_date': create_date,
                                         'author': author,
                                         'category': category,
                                         'text': text,
                                         'comments': comments_to_note,
                                         })


class NoteCreate(LoginRequiredMixin, CreateView):
    form_class = NoteForm
    model = Note
    template_name = 'note_edit.html'
    success_url = ''
    raise_exception = True


class NoteUpdate(LoginRequiredMixin, UpdateView):
    form_class = NoteForm
    model = Note
    template_name = 'note_edit.html'
    raise_exception = True


# удаление объявления
class NoteDelete(LoginRequiredMixin, DeleteView):
    model = Note
    template_name = 'note_delete.html'
    success_url = reverse_lazy('list')
    raise_exception = True


# вьюшка списка откликов автора
@login_required
@csrf_protect
def response(request, **kwargs):
    # обработка изменения статуса отклика
    if request.method == "POST":
        comment_id = request.POST.get('comment_id')
        comment = Comments.objects.get(id=comment_id)
        comment.status = True

        # отправка автору отклика сообщения о подтверждении
        email = comment.author_of_call.email
        subject = 'Ваш отклик одобрен!'
        text_content = (
            f'Объявление: {comment.to_note.header}\n'
            f'Отклик: {comment.text}\n\n  -   Одобрен!'
        )
        html_content = (
            f'Объявление: {comment.to_note.header}<br>'
            f'Отклик: {comment.text}<br><br>  -   Одобрен!'
        )
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        comment.save()

    notes = Note.objects.filter(author=request.user)
    comments = Comments.objects.filter(to_note__in=notes).order_by('-date')

    # фильтр по постам
    if request.method == "GET":
        name = request.GET.get('search')
        if name is not None:
            notes = Note.objects.filter(author=request.user) & Note.objects.filter(header__icontains=name)
            comments = Comments.objects.filter(to_note__in=notes).order_by('-date')

    return render(request, 'response.html', {'comments': comments,
                                             })


# удаление отклика
class CommentDelete(LoginRequiredMixin, DeleteView):
    model = Comments
    template_name = 'comment_delete.html'
    success_url = reverse_lazy('list')
    raise_exception = True