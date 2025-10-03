from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Petition, PetitionVote
from django.db.models import Count, Q

# Create your views here.
def petition_list(request):
    petitions = Petition.objects.annotate(
        upvote_count=Count('votes', filter=Q(votes__vote_type='up'))
    )

    template_data = {
        "title": "Petitions",
        "petitions": petitions
    }
    return render(request, "petitions/petitions.html", {"template_data": template_data})

@login_required
def petition_new(request):
    if request.method == 'POST':
        # get the form data
        title = request.POST.get('title')
        comment = request.POST.get('comment')

        # basic validation
        if title and comment:
            # create the petition
            Petition.objects.create(title=title, description=comment, created_by=request.user)
            return redirect("petition_list")
        else:
            # optionally, show an error message if fields are empty
            template_data = {
                "title": "Create Petition",
                "error": "Both title and comment are required."
            }
            return render(request, "petitions/new.html", {"template_data": template_data})


    template_data = {"title": "Create Petition"}
    return render(request, "petitions/new.html", {"template_data": template_data})  

@login_required
def petition_vote(request, id):
    petition = get_object_or_404(Petition, id=id)

    # Create or update the user's vote
    vote, created = PetitionVote.objects.update_or_create(
        petition=petition,
        user=request.user,
        defaults={'vote_type': PetitionVote.VoteType.UPVOTE},
    )

    if not created:
        vote.delete()
    return redirect('petition_list')