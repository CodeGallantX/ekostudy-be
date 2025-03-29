from django.db import models

# Create your models here.
class Course(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    code = models.CharField(max_length=20, blank=False, null=False)
    unit = models.IntegerField()
    def __str__(self):
        return f"{self.code} - {self.title} - {self.unit} units"