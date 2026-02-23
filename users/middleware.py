from .referrals import track_referral_from_request


class ReferralTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        track_referral_from_request(request)
        return self.get_response(request)
