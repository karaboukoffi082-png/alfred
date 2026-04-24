from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(attrs={'id': 'ratingInput'}),
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Partagez votre expérience...',
                'class': 'w-full border border-gray-200 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition resize-none'
            }),
        }