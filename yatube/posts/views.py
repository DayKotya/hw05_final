from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from .models import Post, Group, Follow
from .forms import PostForm, CommentForm

POSTS_PER_PAGE = 10

User = get_user_model()


@cache_page(20, key_prefix='index_page')
@vary_on_cookie
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.select_related('author', 'group').all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    post_list = group.posts.select_related('author', 'group').all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts_number = user.posts.count()
    user_posts = user.posts.select_related('author', 'group').all()
    paginator = Paginator(user_posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    request_user = request.user
    if request.user.is_authenticated:
        condition = user.following.filter(user=request_user).exists()
        if condition:
            following = True
    context = {
        'username': user,
        'posts_number': posts_number,
        'page_obj': page_obj,
        'following': following,
        'request_user': request_user,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    viewer = request.user
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'count_posts': post.author.posts.count(),
        'viewer': viewer,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    form = PostForm()
    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, 'posts/create_post.html', context)


def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    instance=post,
                    files=request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {'form': form, 'post': post, 'is_edit': True}
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    user_followings = Follow.objects.filter(user=user)
    if author != user and not user_followings.filter(author=author).exists():
        Follow.objects.create(
            user=user,
            author=author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    user_followings = Follow.objects.filter(user=user)
    if user_followings.filter(author=author).exists():
        Follow.objects.filter(author=author).delete()
    return redirect('posts:profile', username)
