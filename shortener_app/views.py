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
            entered_url_title = form.cleaned_data['url_title'] # Get the title from the form

            # Option to handle existing URLs:
            # 1. Try to get an existing URL with the same long_url
            # 2. If found, update its title if the new title is different
            # 3. If not found, create a new URL object with both long_url and url_title

            url_obj, created = URL.objects.get_or_create(
                long_url=long_url,
                defaults={'url_title': entered_url_title} # Set url_title if a new object is created
            )
            
            if not created and url_obj.url_title != entered_url_title:
                # If an existing URL was found and the new title is different, update it.
                # This ensures the most recent title submitted via the form is used.
                url_obj.url_title = entered_url_title
                url_obj.save()


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

        # Retrieve url_title directly from the fetched url_obj
        # Use .url_title if it exists, otherwise provide a default or fallback
        # Changed default to "Your Download" for more general use, but "Your Movie" is fine if context is always movies.
        download_title = url_obj.url_title if url_obj.url_title else "GENERATE DOWNLOAD LINK BELOW" 

        site_config, created = SiteConfiguration.objects.get_or_create(pk=1)
        
        # Initialize active_ads
        active_ads = {}

        # Only fetch and pass ads if global ads are enabled
        if site_config.ads_enabled_globally:
            # Fetch all active ad units, ordered by their location
            ad_units = AdUnit.objects.filter(is_active=True).order_by('location')
            
            # Organize ads by their location for easier template access
            for ad_unit in ad_units:
                if ad_unit.location not in active_ads:
                    active_ads[ad_unit.location] = []
                active_ads[ad_unit.location].append(ad_unit)

        context = {
            'original_download_url': url_obj.long_url,
            'short_code': short_code,
            'url_title': download_title,  # This will now correctly show the input title
            'ads_enabled': site_config.ads_enabled_globally, # Global switch
            'active_ads': active_ads, # Pass active ad units organized by location
        }
        return render(request, 'shortener_app/waiting_page.html', context)
    except Http404:
        # This will be caught by get_object_or_404, but it's good to be explicit
        raise Http404("Short URL not found.") # Or render a custom 404 page
    except Exception as e:
        # Log unexpected errors for debugging
        print(f"An unexpected error occurred: {e}")
        return HttpResponse("An internal server error occurred.", status=500)


def finalize_download(request, short_code):
    try:
        url_obj = get_object_or_404(URL, short_code=short_code)
       
        return redirect(url_obj.long_url)
    except Http404:
        raise Http404("Short URL not found.") # Or render a custom 404 page
    except Exception as e:
        print(f"An unexpected error occurred during finalization: {e}")
        return HttpResponse("An internal server error occurred.", status=500)