from django.shortcuts import render, resolve_url, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, CreateView, DetailView, UpdateView, DeleteView, ListView
from .models import Post, Like
from django.urls import reverse_lazy
from .forms import PostForm, LoginForm, SignUpForm
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required


class OnlyMyPostMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        post = Post.objects.get(id=self.kwargs['pk'])
        return post.author == self.request.user


class Index(TemplateView):
    template_name = 'blogg/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        post_list = Post.objects.all().order_by('-created_at')
        context = {
            'post_list': post_list,
        }
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('blogg:index')

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        return super(PostCreate, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Postを登録しました。')
        return resolve_url('blogg:index')


class PostDatail(DetailView):
    model = Post


class PostUpdate(OnlyMyPostMixin, UpdateView):
    model = Post
    form_class = PostForm

    def get_success_url(self):
        messages.info(self.request, 'Postを更新しました。')
        return resolve_url('blogg:post_detail', pk=self.kwargs['pk'])


class PostDelete(OnlyMyPostMixin, DeleteView):
    model = Post

    def get_success_url(self):
        messages.info(self.request, 'Postを削除しました')
        return resolve_url('blogg:index')


class PostList(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.all().order_by('-created_at')


class Login(LoginView):
    form_class = LoginForm
    template_name = 'blogg/login.html'


class Logout(LogoutView):
    template_name = 'blogg/logout.html'


class Signup(CreateView):
    form_class = SignUpForm
    template_name = 'blogg/signup.html'
    success_url = reverse_lazy('blogg:index')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.object = user
        messages.info(self.request, 'ユーザ登録をしました。')
        return HttpResponseRedirect(self.get_success_url())


@login_required
def Like_add(request, post_id):
    post = Post.objects.get(id=post_id)
    is_liked = Like.objects.filter(
        user=request.user).filter(post=post_id).count()
    if is_liked > 0:
        messages.info(request, '既にお気に入りに追加済みです。')
        return redirect('blogg:post_detail', post_id)
    like = Like()
    like.user = request.user
    like.post = post
    like.save()

    messages.success(request, 'お気に入りに追加しました!')
    return redirect('blogg:post_detail', post.id)
