from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Petition(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
    
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
    )

class PetitionVote(models.Model):
    class VoteType(models.TextChoices):
        UPVOTE = "up", "Upvote"
        DOWNVOTE = "down", "Downvote"
    
    petition = models.ForeignKey(
        "Petition", on_delete=models.CASCADE, related_name="votes"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote_type = models.CharField(
        max_length=5,
        choices=VoteType.choices,
        default=VoteType.UPVOTE,
    )

    class Meta:
        unique_together = ("petition", "user")

    def __str__(self):
        return f"{self.user.username} voted {self.vote_type} on {self.petition.title}"