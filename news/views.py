from django.shortcuts import render, redirect
from datetime import datetime
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from .models import Post, Category, PostCategory
from .filters import PostFilter
from django.core.paginator import Paginator
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail


class NewsList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-id')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['time_now'] = datetime.utcnow()
        return context


class NewsDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'
    queryset = Post.objects.all()


# для страницы с фильтром (поиск)
class FilterPostView(ListView):
    model = Post
    template_name = 'posts_filter.html'
    context_object_name = 'posts_filter'
    paginate_by = 10

    # общий метод для создания дополнительных атрибутов
    # (где-то во views уже был, надо разобраться вообще как это работает, ибо я хз)
    def get_context_data(self, **kwargs):
        # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса
        # на самом деле не понятно вообще ничего. Что происходит то?
        context = super().get_context_data(**kwargs)
        # вписываем наш фильтр в контекст (что бы это ни значило)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


# дженерик для создания объекта. Надо указать только имя шаблона и класс формы, который мы написали в прошлом юните. Остальное он сделает за вас
class PostCreateView(CreateView, PermissionRequiredMixin, LoginRequiredMixin):
    template_name = 'new_create.html'
    permission_required = ('new_create.html')
    form_class = PostForm

    def mail_post(self, request, *args, **kwargs):
        send_mail(
            subject=f'{Post.name_news}',
            message='Привет, новая статья в твоем разделе!',
            from_email='masian4eg@yandex.ru',
            recipient_list=['maxi4eg@mail.ru']
        )


# дженерик для редактирования объекта
class PostUpdateView(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    template_name = 'new_create.html'
    form_class = PostForm
    login_required = ('new_update`')
    permission_required = ('new_update`')

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


# дженерик для удаления товара
class PostDeleteView(DeleteView):
    template_name = 'new_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'protect/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        context['is_auth'] = self.request.user.is_authenticated
        return context


@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')


@login_required
def subscribe_category(request):
    user = request.user  # получаем из реквеста самого пользователя
    cat_id = request.POST['cat_id']  # получаем из реквеста то, что пришло из формы через ПОСТ
    category = Category.objects.get(pk=int(cat_id))  # получаем категорию через cat_id, который пришёл через ПОСТ через скрытое поле

    # если связь пользователя с категорией не создана,
    # второй вариант - проверять имя кнопки, которая пришла с реквестом
    # и условие строить уже на этом
    if user not in category.subscribed_users.all():
        # добавляем пользователя в связь с категорией
        category.subscribed_users.add(user)

    # а если связь уже есть, то отписываем, т.е. удаляем из этой связи
    else:
        category.subscribed_users.remove(user)

    # после чего возвращаем на предыдущую страницу, которую берём из реквеста
    # она хранится в META, а это словарь, поэтому достаём через гет
    # если этого ключа нет, то возвращается рут и редирект кидает в корень
    return redirect(request.META.get('HTTP_REFERER', '/'))
