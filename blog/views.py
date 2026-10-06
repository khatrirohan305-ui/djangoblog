from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import PostForm
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
    post = get_object_or_404(Post, slug=slug)
    # drafts are visible to staff only
    if post.status != "published" and not request.user.is_staff:
        raise Http404
    return render(request, 'blog/post_details.html', {'post': post})


def about(request):
    return render(request, "blog/about.html", {"title": "DjangoBlog"})


def contact(request):
    return render(request, "blog/contact.html", {"title": "DjangoBlog"})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def get_success_url(self):
        return reverse_lazy("post_detail", kwargs={"slug": self.object.slug})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def get_success_url(self):
        return reverse_lazy("post_detail", kwargs={"slug": self.object.slug})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("home")