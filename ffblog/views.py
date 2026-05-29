from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from .models import Post, Category, Comment, ContactMessage
from .forms import PostForm, RegisterForm, CommentForm

def home(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    categories = Category.objects.all()

    if query:
        posts = Post.objects.filter(
            status="published",
            title__icontains=query
        ).order_by("-created_at") | Post.objects.filter(
            status="published",
            body__icontains=query
        ).order_by("-created_at")
    elif category_slug:
        posts = Post.objects.filter(
            status="published",
            category__slug=category_slug
        ).order_by("-created_at")
    else:
        posts = Post.objects.filter(status="published").order_by("-created_at")

    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "ffblog/post_list.html", {
        "posts": page_obj,
        "categories": categories,
        "selected_category": category_slug,
        "page_obj": page_obj,
    })

def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    comments = post.comments.all().order_by('-created_at')

    if request.method == 'POST':
        body = request.POST.get('body')
        name = request.POST.get('name', 'Anonymous')
        if body:
            Comment.objects.create(
                post=post,
                name=name,
                email='',
                body=body
            )
            return redirect('post_detail', pk=post.id)

    is_liked = False
    if request.user.is_authenticated:
        is_liked = post.likes.filter(id=request.user.id).exists()

    return render(request, 'ffblog/post_detail.html', {
        'post': post,
        'comments': comments,
        'is_liked': is_liked,
        'total_likes': post.total_likes(),
    })

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('post_detail', pk=post.id)

def delete_comment(request, pk):
    comment = get_object_or_404(Comment, id=pk)
    post_id = comment.post.id
    comment.delete()
    return redirect('post_detail', pk=post_id)

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'ffblog/create_post.html', {'form': form})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'ffblog/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'ffblog/delete_post.html', {'post': post})

def logout_view(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def about(request):
    return render(request, 'ffblog/about.html')

def contact(request):
    success = False
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            success = True
    return render(request, 'ffblog/contact.html', {'success': success})

class HomeView(ListView):
    model = Post
    template_name = 'home.html'