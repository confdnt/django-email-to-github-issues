import json
from django.http import JsonResponse

def github_webhook(request):
    # Optional: Handle webhook events
    payload = json.loads(request.body)
    return JsonResponse({'status': 'success'})
