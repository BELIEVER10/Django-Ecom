from django import forms
from .models import WebsiteReview

class WebsiteReviewForm(forms.ModelForm):
    class Meta:
        model = WebsiteReview
        fields = ['title', 'description', 'rating', 'profile_pic', 'professional_title', 'institution']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Amazing sound journey experience...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Share your detailed experience with our website...'
            }),
            'rating': forms.RadioSelect(choices=WebsiteReview._meta.get_field('rating').choices),
            'professional_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Sound Therapist, Yoga Instructor'
            }),
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., International Sound Healing Association'
            }),
        }
        labels = {
            'title': 'Review Headline',
            'description': 'Detailed Review',
            'rating': 'Tap to rate (1 to 5)',
            'profile_pic': 'Profile Picture',
            'professional_title': 'Professional Title / Practice Area',
            'institution': 'Institution / Community',
        }
        help_texts = {
            'profile_pic': 'Upload a photo to personalize your review (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make rating field use star icons via custom template
        self.fields['rating'].widget.attrs.update({'class': 'star-rating'})