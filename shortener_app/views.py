from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from .models import URL, SiteConfiguration, AdUnit # Ensure all models are imported
from .forms import URLShortenForm

def create_short_url(request):
    shortened_url = None # Initialize variable to hold the shortened URL
    if request.method == 'POST':
        form = URLShortenForm(request.POST)
        if form.is_valid():
            long_url = form.cleaned_data['long_url']
            # Try to get an existing URL object or create a new one
            url_obj, created = URL.objects.get_or_create(long_url=long_url)
            # Construct the full shortened URL for display
            # request.build_absolute_uri('/') gives you the base URL of your site (e.g., http://127.0.0.1:8000/)
            shortened_url = request.build_absolute_uri('/') + url_obj.short_code
            # Render the same page, but now with the form and the new shortened URL
            return render(request, 'shortener_app/create_short_url.html', {'form': form, 'shortened_url': shortened_url})
    else:
        # If it's a GET request, just display an empty form
        form = URLShortenForm()
    # Render the initial page or the page with the shortened URL
    return render(request, 'shortener_app/create_short_url.html', {'form': form})

def redirect_to_download(request, short_code):
    try:
        url_obj = get_object_or_404(URL, short_code=short_code)
        url_obj.clicks += 1
        url_obj.save()

        site_config, created = SiteConfiguration.objects.get_or_create(pk=1)
        
        # Initialize active_ads
        active_ads = {}

        # Only fetch and pass ads if global ads are enabled
        if site_config.ads_enabled_globally:
            # Fetch all active ad units, ordered by their location
            # We'll group them by location in the template
            ad_units = AdUnit.objects.filter(is_active=True).order_by('location')
            
            # Organize ads by their location for easier template access
            for ad_unit in ad_units:
                if ad_unit.location not in active_ads:
                    active_ads[ad_unit.location] = []
                active_ads[ad_unit.location].append(ad_unit)

        context = {
            'original_download_url': url_obj.long_url,
            'short_code': short_code,
            'ads_enabled': site_config.ads_enabled_globally, # Global switch
            'active_ads': active_ads, # Pass active ad units organized by location
        }
        return render(request, 'shortener_app/waiting_page.html', context)
    except Http404:
        return HttpResponse("Short URL not found.", status=404)


def finalize_download(request, short_code):
    try:
        url_obj = get_object_or_404(URL, short_code=short_code)
       
        return redirect(url_obj.long_url)
    except Http404:
        return HttpResponse("Short URL not found.", status=404)
    
    