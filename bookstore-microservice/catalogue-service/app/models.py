from django.db import models


class Placeholder(models.Model):
    """Placeholder model to keep app migrations simple; can be removed when real models are added."""

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

