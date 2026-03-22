from django.contrib.auth.models import User

def contagem_pendentes(request):
    if request.user.is_authenticated and request.user.is_staff:
        # Conta quantos usuários estão inativos (is_active=False)
        count = User.objects.filter(is_active=False).count()
        return {'pendentes_count': count}
    return {'pendentes_count': 0}