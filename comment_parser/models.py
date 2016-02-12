from django.db import models

class Comment(models.Model):

    project_name = models.CharField(max_lenght=200)
    original_comment_text = models.TextField()
    treated_comment_text = models.TextField()
    start_line = models.IntegerField()
    end_line = models.IntegerField()
    design_classification = models.CharField(max_lenght=200)
    requirement_classification = models.CharField(max_lenght=200)


