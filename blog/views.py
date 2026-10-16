from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import PostForm, RegisterForm
from .models import Category, Post


def home(request):
    posts_list = (
        Post.objects.filter(status="published")
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at")
    )

    # optional filter: /?category=<id>
    selected_category = request.GET.get("category")
    if selected_category and selected_category.isdigit():
        posts_list = posts_list.filter(category_id=selected_category)

    paginator = Paginator(posts_list, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        'title': 'Hello Djangoblog',
        'page_obj': page_obj,
        'posts': page_obj,
        'categories': Category.objects.all(),
        'selected_category': selected_category,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    # Published posts are visible to everyone.
    # Drafts are visible only to their author (and staff).
    visible = Q(status="published")
    if request.user.is_authenticated:
        visible = visible | Q(author=request.user)
        if request.user.is_staff:
            visible = Q()  # staff can see everything
    post = get_object_or_404(Post.objects.filter(visible), slug=slug)
    return render(request, 'blog/post_details.html', {'post': post})


def about(request):
    return render(request, "blog/about.html", {"title": "DjangoBlog"})


def contact(request):
    return render(request, "blog/contact.html", {"title": "DjangoBlog"})


def custom_403(request, exception=None):
    return render(request, "blog/403.html", status=403)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "blog/register.html"
    success_url = "/"

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    login_url = "login"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Post published successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("post_detail", kwargs={"slug": self.object.slug})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    login_url = "login"

    def test_func(self):
        return self.get_object().author == self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Post updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("post_detail", kwargs={"slug": self.object.slug})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    login_url = "login"
    success_url = reverse_lazy("home")

    def test_func(self):
        return self.get_object().author == self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Post deleted.")
        return super().form_valid(form)


class MyPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "blog/my_posts.html"
    paginate_by = 6
    login_url = "login"

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by("-created_at")


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    paginate_by = 6

    def get_queryset(self):
        qs = Post.objects.filter(status="published").order_by("-created_at")
        category_slug = self.request.GET.get("category")
        if category_slug:
            qs = qs.filter(category__name__iexact=category_slug)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context4
    from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Post

class MyPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "blog/my_posts.html"
    context_object_name = "posts"

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by("-created_at")