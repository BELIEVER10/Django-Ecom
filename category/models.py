from django.db import models
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category_image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('product_by_category', args=[self.slug])
    
    def price_search_url(self):
        return reverse('search_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name

class LeftBanner(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='banner/left_banner')

    def __str__(self):
        return self.name
    
class RightBanner(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='banner/right_banner')

    def __str__(self):
        return self.name
    

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} - {self.subject or 'No Subject'}"

    class Meta:
        ordering = ['-timestamp']


from django.db import models

class MainCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Main Categories"

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)  # for URLs

    class Meta:
        verbose_name_plural = "Sub Categories"

    def get_url(self):
        return reverse('store_by_subcategory', args=[self.slug])

    def __str__(self):
        return self.name
