from django.db import models

class Submissions(models.Model):
    # title of submission
    title = models.CharField(max_length=300, null=False)
    # user who made the post
    poster = models.CharField(max_length=20, null=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "\"{}\" posted by: \\u\\{}".format(self.title, self.poster)