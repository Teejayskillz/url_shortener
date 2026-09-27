import sys
import copy
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.core.signing import TimestampSigner
from shortener_app.models import URL, SiteConfiguration

# Python 3.14 compatibility patch for Django 5.2 test client Context copying
from django.template.context import BaseContext, Context
if sys.version_info >= (3, 14):
    def _patched_context_copy(self):
        obj = Context()
        obj.dicts = [d.copy() for d in self.dicts]
        return obj
    BaseContext.__copy__ = _patched_context_copy


class VIPAdFreeAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url_obj = URL.objects.create(
            long_url="https://example.com/files/movie.mp4",
            url_title="Test Movie 1080p",
            short_code="testvip"
        )
        self.site_config = SiteConfiguration.objects.create(
            pk=1,
            ads_enabled_globally=True
        )

    def test_valid_vip_token_grants_ad_free_access(self):
        signer = TimestampSigner(key=settings.CDN_SHARED_SECRET)
        token = signer.sign("42")

        url = reverse('redirect_to_download', kwargs={'short_code': self.url_obj.short_code})
        response = self.client.get(f"{url}?token={token}")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_vip_ad_free'])
        self.assertEqual(response.context['vip_user_id'], "42")
        self.assertFalse(response.context['ads_enabled'])
        self.assertIn("VIP Ad-Free Mode Activated", response.content.decode('utf-8'))
        self.assertIn("NZDWorld Main Blog", response.content.decode('utf-8'))

    def test_invalid_or_tampered_token_denies_vip_access(self):
        tampered_token = "42:1xAr3Z:invalid_signature_hash"

        url = reverse('redirect_to_download', kwargs={'short_code': self.url_obj.short_code})
        response = self.client.get(f"{url}?token={tampered_token}")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_vip_ad_free'])
        self.assertIsNone(response.context['vip_user_id'])
        self.assertTrue(response.context['ads_enabled'])

    def test_missing_token_defaults_to_regular_access(self):
        url = reverse('redirect_to_download', kwargs={'short_code': self.url_obj.short_code})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_vip_ad_free'])
        self.assertIsNone(response.context['vip_user_id'])
        self.assertTrue(response.context['ads_enabled'])
