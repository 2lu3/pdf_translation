from django.core.validators import FileExtensionValidator
from django.db import models

class PDFDocument(models.Model):
    document = models.FileField(upload_to='documents/', validators=[FileExtensionValidator(['pdf',])])
    uploaded_at = models.DateTimeField(auto_now_add=True)
