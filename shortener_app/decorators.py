from functools import wraps
from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired


def ad_free_vip_required(view_func):
    """
    Decorator for CDN / URL Shortener views to authenticate VIP users.

    Reads `token` query parameter from `request.GET`.
    Uses `TimestampSigner(key=settings.CDN_SHARED_SECRET)` to unsign the token with `max_age=300` (5-minute expiration window).

    If valid:
        Sets `request.is_vip_ad_free = True` and `request.vip_user_id = user_id`.
    If invalid, tampered, or missing:
        Sets `request.is_vip_ad_free = False` and `request.vip_user_id = None`.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.GET.get('token')
        is_vip = False
        vip_user_id = None

        if token:
            secret_key = getattr(settings, 'CDN_SHARED_SECRET', getattr(settings, 'SECRET_KEY', ''))
            signer = TimestampSigner(key=secret_key)
            try:
                # Unsign token enforcing a 5-minute (300 seconds) expiration window
                vip_user_id = signer.unsign(token, max_age=300)
                is_vip = True
            except (BadSignature, SignatureExpired):
                is_vip = False
                vip_user_id = None

        request.is_vip_ad_free = is_vip
        request.vip_user_id = vip_user_id
        return view_func(request, *args, **kwargs)

    return _wrapped_view
