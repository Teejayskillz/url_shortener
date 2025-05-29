
from django import forms

class URLShortenForm(forms.Form):
    long_url = forms.URLField(
        label="Enter Long URL",
        max_length=2000,
        widget=forms.URLInput(attrs={'placeholder': 'e.g., https://example.com/very/long/download/link.zip'})
    )