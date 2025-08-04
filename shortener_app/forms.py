
from django import forms

class URLShortenForm(forms.Form):
    url_title = forms.CharField(
        label="Enter URL Title",
        max_length=600,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Download M3gan (2025) Movie'})
    )
    long_url = forms.URLField(
        label="Enter Long URL",
        max_length=2000,
        widget=forms.URLInput(attrs={'placeholder': 'e.g., https://example.com/very/long/download/link.zip'})
    )