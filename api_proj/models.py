from django.db import models

# Create your models here.

class Keys(models.Model):
    key_name = models.CharField(max_length=255, unique=True)
    key = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.key_name} created at {self.created_at}"

class History(models.Model):
    key = models.ForeignKey(Keys, on_delete=models.CASCADE, related_name='history')
    timestamp = models.DateTimeField(auto_now_add=True)
    input = models.TextField()
    output = models.TextField()

    def __str__(self):
        return f"{self.key.key_name} - {self.input}, {self.output} at {self.timestamp}"
