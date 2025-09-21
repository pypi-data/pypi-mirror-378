from django.db import models

class AutocompleteEntry(models.Model):
    name = models.CharField(max_length=100)
    module_path = models.CharField(max_length=255)
    class_name = models.CharField(max_length=100, blank=True)
    is_function = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('name', 'module_path')
    
    def __str__(self):
        return f"{self.name} ({self.module_path})"