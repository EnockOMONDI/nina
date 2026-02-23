from django.db.models import F, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, Post


def blog_list(request):
    posts = (
        Post.objects.filter(status="published")
        .select_related("category", "user")
        .prefetch_related("tags")
    )
    featured = posts.filter(featured=True)[:3]
    trending = posts.filter(trending=True)[:5]
    categories = Category.objects.filter(active=True)
    context = {
        "posts": posts,
        "featured_posts": featured,
        "trending_posts": trending,
        "categories": categories,
    }
    return render(request, "blog/blog_list.html", context)


def blog_search(request):
    query = request.GET.get("q", "").strip()
    posts = Post.objects.filter(status="published")
    if query:
        posts = posts.filter(
            Q(title__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(content__icontains=query)
        )
    context = {"posts": posts, "query": query}
    return render(request, "blog/blog_search.html", context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, active=True)
    posts = Post.objects.filter(status="published", category=category)
    context = {"category": category, "posts": posts}
    return render(request, "blog/category_detail.html", context)


def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status="published")
    Post.objects.filter(pk=post.pk).update(views=F("views") + 1)
    post.refresh_from_db(fields=["views"])
    context = {"post": post}
    return render(request, "blog/blog_detail.html", context)


def blog_detail_redirect(request, pid):
    post = get_object_or_404(Post, pid=pid)
    return redirect("blog-detail", slug=post.slug)


def blog_rss(request):
    return HttpResponse("RSS feed will be available here.", content_type="text/plain")


def blog_sitemap(request):
    return HttpResponse("Blog sitemap will be available here.", content_type="text/plain")
