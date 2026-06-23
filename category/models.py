from django.db import models
from django.urls import reverse
from django.utils.text import slugify

# Create your models here.


    

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
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Main Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

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
    

class InsideSubCategory(models.Model):
    sub_category = models.ForeignKey(SubCategory, related_name='insidesubcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)  # Add this field

    class Meta:
        verbose_name_plural = "Inside Sub Categories"

    def __str__(self):
        return self.name

    def get_url(self):
        # URL that shows products belonging to this inside subcategory
        return reverse('products_by_inside_subcategory', args=[self.sub_category.slug, self.slug])

    

