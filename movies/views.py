from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, ReviewLike
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, OuterRef

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    user = request.user if request.user.is_authenticated else None
    reviews_qs = Review.objects.filter(movie=movie).select_related('user')
    reviews_qs = reviews_qs.annotate(like_count=Count('likes', distinct=True))
    if user:
        reviews_qs = reviews_qs.annotate(
            liked_by_me=Exists(
                ReviewLike.objects.filter(review=OuterRef('pk'), user=user)
            )
        )
    reviews = reviews_qs.order_by('-like_count', '-date')

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

def top_reviews(request):
    user = request.user if request.user.is_authenticated else None
    reviews_qs = Review.objects.select_related('user', 'movie').annotate(like_count=Count('likes', distinct=True))
    if user:
        reviews_qs = reviews_qs.annotate(
            liked_by_me=Exists(
                ReviewLike.objects.filter(review=OuterRef('pk'), user=user)
            )
        )
    reviews = reviews_qs.order_by('-like_count', '-date')[:20]

    template_data = {}
    template_data['title'] = 'Top Reviews'
    template_data['reviews'] = reviews
    return render(request, 'movies/top_reviews.html', {'template_data': template_data})

@login_required
def like_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    ReviewLike.objects.get_or_create(review=review, user=request.user)
    return redirect('movies.show', id=review.movie.id)

@login_required
def unlike_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    ReviewLike.objects.filter(review=review, user=request.user).delete()
    return redirect('movies.show', id=review.movie.id)