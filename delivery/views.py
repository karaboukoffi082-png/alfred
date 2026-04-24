from django.views import View
from django.http import HttpResponse

class OrderTrackingView(View):
    def get(self, request):
        return HttpResponse("Tracking page")