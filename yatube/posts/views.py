from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    index_page = True
    context = {
        'page_obj': page_obj,
        'index_page': index_page,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.filter(group=group).all()
    paginator = Paginator(posts, settings.PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    name = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=name).order_by('-pub_date').all()
    paginator = Paginator(post_list, settings.PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    follow = Follow.objects.filter(
        user__username=request.user,
        author=name
    ).exists()
    context = {
        'name': name,
        'post_list': post_list,
        'page_obj': page_obj,
        'follow': follow,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    username = post.author
    post_list = Post.objects.filter(author=username).all()
    form = CommentForm()
    context = {
        'post': post,
        'post_list': post_list,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST, instance=post)
    return render(request, 'posts/create_post.html', {'form': form,
                                                      'post': post, })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follows = User.objects.filter(following__user=request.user).all()
    post_list = Post.objects.filter(author__in=follows).all()
    paginator = Paginator(post_list, settings.PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    index_page = True
    context = {
        'page_obj': page_obj,
        'index_page': index_page}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=author
    ).delete()
    return redirect('posts:profile', username=username)
