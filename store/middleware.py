class CurrencyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set default currency only if not already set
        if 'currency' not in request.session:
            request.session['currency'] = 'USD'
        return self.get_response(request)
