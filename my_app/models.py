from django.db import models
from django.contrib.postgres.fields import ArrayField

class Submissions(models.Model):
    # title of submission
    title = models.CharField(max_length=300, null=False, blank=False)
    # user who made the post
    poster = models.CharField(max_length=20, null=False, blank=False)
    # date when post was queried
    queried_at = models.DateTimeField(auto_now_add=True)
    # submission id
    submission_id = models.CharField(max_length=7, null=False, blank=False)
    # subreddit where the submission was made
    subreddit = models.CharField(max_length=20, null=False, blank=False)
    # number of comments
    num_comments = models.IntegerField(null=False, blank=False)
    # sha256 of all comments in the submission
    sha256 = models.CharField(max_length=64, null=False, blank=False)

    class Meta:
        ordering = ['id', 'queried_at']
        constraints = [
            models.UniqueConstraint(fields= ['sha256'], name='unique comment state'),
        ]

    def __str__(self):
        return "\"{}\" posted by: /u/{}".format(self.title, self.poster)