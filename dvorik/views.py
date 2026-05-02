from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


def handler403(request, exception):
    return render(request, '403.html', status=403)


def healthz(request):
    """Liveness/readiness probe — verifies DB connectivity."""
    try:
        with connection.cursor() as cur:
            cur.execute('SELECT 1')
            cur.fetchone()
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=503)
    return JsonResponse({'ok': True})
