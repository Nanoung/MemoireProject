from .models import Client

def client_context(request):
    client = None
    client_id = request.session.get('client_id')
    if client_id:
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            pass
    return {'client_session': client}