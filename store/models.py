from django.db import models
from category.models import Category, SubCategory
from django.urls import reverse

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=255, unique=True)
    model_number = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    sub_description = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='photos/products')
    price = models.IntegerField()
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    is_new_arrival = models.BooleanField(default=False)
    is_left_banner_offer = models.BooleanField(default=False)
    is_right_banner_offer = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)  # NEW FIELD
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, blank=True, null=True)


    def get_url(self):
        return reverse('product_detail', args=[self.sub_category.slug, self.slug])

    def __str__(self):
        return self.product_name


class CarouselItem(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='carousel_images/')
    slug = models.SlugField(blank=True)
    

    def __str__(self):
        return self.title or "Carousel Item"
    


variation_category_choice = (
    ('size', 'size'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=200, choices=variation_category_choice, blank=True, null=True)
    variation_value = models.CharField(max_length=200, blank=True, null=True)
    model_number = models.CharField(max_length=100, null=True, blank=True)
    sub_description = models.TextField(blank=True)
    price = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

 

    def __str__(self):
        return self.variation_value


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=None)
    image = models.ImageField(upload_to='store/products', max_length=255)

    class Meta:
        verbose_name = 'product gallery'
        verbose_name_plural = 'product gallery'


    def __str__(self):
        return self.product.product_name