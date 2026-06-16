from django.db import models
from category.models import MainCategory, SubCategory, InsideSubCategory
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from cloudinary.models import CloudinaryField
from storage_backends import VariationSoundStorage

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=255, unique=True)
    model_number = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    sub_description = CKEditor5Field(config_name='extends',  null=True, blank=True)
    description = CKEditor5Field(config_name='extends', null=True, blank=True)
    image = CloudinaryField('image', folder='photos/products')
    # price = models.IntegerField()
    price = models.IntegerField(null=True, blank=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    is_new_arrival = models.BooleanField(default=False)
    is_left_banner_offer = models.BooleanField(default=False)
    is_right_banner_offer = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)  # NEW FIELD
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, null=True, blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, blank=True, null=True)
    inside_sub_category = models.ForeignKey(InsideSubCategory, on_delete=models.CASCADE, blank=True, null=True)


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
    sound_file = models.FileField(
        upload_to='variation_sounds/',
        blank=True,
        null=True,
        verbose_name="Sound File",
        storage=VariationSoundStorage()
    )
    model_number = models.CharField(max_length=100, null=True, blank=True)
    stock = models.IntegerField(null=True, blank=True)
    sub_description = CKEditor5Field(config_name='extends')
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


from django.db import models
from accounts.models import Account
from django.core.validators import MinValueValidator, MaxValueValidator

class WebsiteReview(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='website_reviews')
    title = models.CharField(max_length=200, verbose_name="Review Headline")
    description = models.TextField(verbose_name="Detailed Review")
    rating = models.FloatField()
    profile_pic = models.ImageField(
        upload_to='review_profiles/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Profile Picture"
    )
    professional_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Professional Title / Practice Area"
    )
    institution = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Institution / Community"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Website Review"
        verbose_name_plural = "Website Reviews"

    def __str__(self):
        return f"{self.title} by {self.user.full_name() or self.user.username}"


from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Gallery(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    cover_image = models.ImageField(upload_to='gallery/covers/')
    description = models.TextField(blank=True, help_text="Short description of the gallery")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'gallery'
        verbose_name_plural = 'gallery'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('gallery_detail', args=[self.slug])

    def __str__(self):
        return self.title

class GalleryImage(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='gallery/images/')
    title = models.CharField(max_length=200, blank=True, help_text="Optional title for this image")
    description = models.TextField(blank=True, help_text="Detailed description of this image")
    # Optional: order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.gallery.title} - {self.title or self.pk}"