from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from .models import Post, Tag, PostLike, PostComment, PostCommentLike
from game_features.models import Category
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PostForm, EmailSubscriptionForm
from django.contrib import messages
import logging
from django.urls import reverse
from users.models import MyUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .forms import PostCommentForm, CommentReplyForm
from django.contrib import messages
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)


# Create your views here.
class PostListView(ListView):
    model = Post
    template_name = 'blog/blog.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all().order_by('-frequency')[:10]

        # them form (huyen)
        context['subscription_form'] = EmailSubscriptionForm()


        return context

    # huyen lao nhao
    def post(self, request, *args, **kwargs): 
        subscription_form = EmailSubscriptionForm(request.POST)

        if subscription_form.is_valid():
            subscription_form.save()
            return redirect(request.path)  # avoid resubmission on reload
        
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context['subscription_form'] = subscription_form
        return self.render_to_response(context)



class UserPostListView(ListView):
    model = Post
    template_name = 'blog/blog.html'
    context_object_name = 'posts'
    ordering = ['-updated_at']
    paginate_by = 10
    
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        user = get_object_or_404(MyUser, pk=pk)
        return Post.objects.filter(user=user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all().order_by('-frequency')[:10]
        return context


class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/blog.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 10
    
    def get_queryset(self):
        slug = self.kwargs.get('slug')
        
        category = get_object_or_404(Category, slug=slug)
        return Post.objects.filter(category=category).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all().order_by('-frequency')[:10]
        return context
    
    
    
class TagPostListView(ListView):
    model = Post
    template_name = 'blog/blog.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 10
    
    def get_queryset(self):
        slug = self.kwargs.get('slug')
        
        print(slug)
        
        tag = get_object_or_404(Tag, slug=slug)
        return Post.objects.filter(tags__in=[tag]).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all().order_by('-frequency')[:10]
        return context    
    

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/blog-detail.html'
    
    def get_context_data(self, **kwargs):
        user = self.request.user
        obj = self.get_object()
        obj.count_view += 1
        obj.save()
        
        context = super().get_context_data(**kwargs)
        related_posts = Post.objects.all().order_by('created_at')[:3]
        
        context['comment_form'] = PostCommentForm(user=user, post=obj)
        context['reply_form'] = CommentReplyForm(user=user, post=obj)

        comments = PostComment.objects.filter(post=obj).order_by('-created_at')
        
        if user.is_authenticated:
            if PostLike.objects.filter(user=user, post=obj).exists():
                context['post_liked'] = 'post_liked'
                
            user_comment_likes = PostCommentLike.objects.filter(user=user, comment__in=comments)
            liked_comment_ids = set(user_comment_likes.values_list('comment_id', flat=True))
        
            context['liked_comment_ids'] = liked_comment_ids
        
        # paginator
        paginator = Paginator(comments, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        
        context['tags'] = Tag.objects.all().order_by('-frequency')[:10]
        context['related_posts'] = related_posts
        return context
    
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.request.user
        post = self.object
        parent_id = request.POST.get('parent_id')
        
        parent_comment = None
        if parent_id:
            try:
                parent_comment = PostComment.objects.get(pk=parent_id)
            except PostComment.DoesNotExist:
                parent_comment = None
        
        comment_form = PostCommentForm(request.POST, user=user, post=post)
        reply_form = CommentReplyForm(request.POST, user=user, post=post, comment=parent_comment)
        
        if parent_comment and reply_form.is_valid():
            reply_form.save()
            return redirect('post-detail', post.pk)
        elif not parent_id and comment_form.is_valid():
            comment_form.save()
            return redirect('post-detail', post.pk)
        else:
            print(f'Comment Form Error: {comment_form.errors}')
            print(f'Reply Form Error: {reply_form.errors}')
                        
        context = self.get_context_data()
        context['comment_form'] = comment_form
        context['reply_form'] = reply_form
        messages.error(request, "There was an error with your comment.")
        return self.render_to_response(context)

    
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create-post.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.user = self.request.user
        post.save()
        
        self.object = post

        tag_str = form.cleaned_data.get('tags', '')
        tag_list = [t.strip().lstrip('#') for t in tag_str.split(' ') if t.strip()]
        tag_objects = []
        for tag_name in tag_list:
            if len(tag_name) < 3:
                messages.error(self.request, f"Tag '{tag_name}' too short.")
                return self.form_invalid(form)
            tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
            tag_obj.frequency += 1
            tag_obj.save()
            tag_objects.append(tag_obj)

        post.tags.set(tag_objects)

        messages.success(self.request, "Post created successfully!")
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse('post-detail', kwargs={'pk': self.object.pk})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_reaction(request):
    user = request.user
    post_pk = request.data.get('post_pk')
    action = request.data.get('action')
    
    if action not in ['liked', 'unlike']:
        return Response({'error': 'Invalid action.'}, status=400)
    
    try:
        post = Post.objects.get(pk=post_pk)
        
        print(post)
    except Post.DoesNotExist:
        return Response({'error': 'Post does not exits.'}, status=400)
    
    if action == 'liked':
        try:
            PostLike.objects.create(user=user, post=post)
        except Exception as e:
            return Response({'error': f'An exception while being like post({str(e)})', 'message': str(e)}, status=400)
    else:
        try:
            post_like = PostLike.objects.get(user=user, post=post)
        except PostLike.DoesNotExist:
            return Response({'error': 'Post Like does not exists.'}, status=400)
        try:
            post_like.delete()
        except Exception as e:
            return Response({'error': 'An exception while deleting PostLike.', 'message': str(e)}, status=200)
    
    return Response({'success': True, 'message': f'Do {action} successfully.'}, status=200)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_comment_reaction(request):
    user = request.user
    comment_pk = request.data.get('comment_pk')
    action = request.data.get('action')
    
    if action not in ['liked', 'unlike']:
        return Response({'error': 'Invalid action.'}, status=400)
    
    try:
        comment = PostComment.objects.get(pk=comment_pk)
    except PostComment.DoesNotExist:
        return Response({'error': 'PostComment does not exits.'}, status=400)
    
    if action == 'liked':
        try:
            PostCommentLike.objects.create(user=user, comment=comment)
        except Exception as e:
            return Response({'error': 'An exception while being like comment.', 'message': str(e)}, status=400)
    else:
        try:
            comment_like = PostCommentLike.objects.get(user=user, comment=comment)
        except PostCommentLike.DoesNotExist:
            return Response({'error': 'PostCommentLike does not exists.'}, status=400)
        try:
            comment_like.delete()
        except Exception as e:
            return Response({'error': 'An exception while deleting PostCommentLike.', 'message': str(e)}, status=200)
    
    return Response({'success': True, 'message': f'Do {action} successfully.'}, status=200)