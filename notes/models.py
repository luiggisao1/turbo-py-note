from django.db import models
from django.conf import settings

class Note(models.Model):
    CATEGORY_CHOICES = [
        ('random', 'Random Thoughts'),
        ('personal', 'personal'),
        ('school', 'school'),
        ('drama', 'drama'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notes')
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title