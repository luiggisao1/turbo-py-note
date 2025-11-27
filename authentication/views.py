from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@csrf_exempt
@require_POST
def register(request):
    try:
        if request.content_type and request.content_type.startswith('application/json'):
            payload = json.loads(request.body.decode() or '{}')
            email = payload.get('email')
            password = payload.get('password')
        else:
            email = request.POST.get('email')
            password = request.POST.get('password')
    except Exception:
        return HttpResponseBadRequest('Invalid request body')

    if not email or not password:
        return HttpResponseBadRequest('Email and password are required')

    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'error': 'User with this email already exists'}, status=400)

    username_field = getattr(User, 'USERNAME_FIELD', 'username')
    create_kwargs = {}
    if username_field == 'email':
        create_kwargs['email'] = email
    else:
        create_kwargs['username'] = email
        create_kwargs['email'] = email

    user = User.objects.create_user(password=password, **create_kwargs)

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    return JsonResponse({'id': user.pk, 'email': getattr(user, 'email', ''), 'access': access_token, 'refresh': refresh_token}, status=201)

@csrf_exempt
@require_POST
def login_view(request):
    try:
        if request.content_type and request.content_type.startswith('application/json'):
            payload = json.loads(request.body.decode() or '{}')
            email = payload.get('email')
            password = payload.get('password')
        else:
            email = request.POST.get('email')
            password = request.POST.get('password')
    except Exception:
        return HttpResponseBadRequest('Invalid request body')

    if not email or not password:
        return HttpResponseBadRequest('Email and password are required')

    username_field = getattr(User, 'USERNAME_FIELD', 'username')
    if username_field == 'email':
        user = authenticate(request, email=email, password=password)
    else:
        user = authenticate(request, username=email, password=password)

    if user is None:
        return JsonResponse({'error': 'Invalid credentials'}, status=400)

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    return JsonResponse({'id': user.pk, 'email': getattr(user, 'email', ''), 'access': access_token, 'refresh': refresh_token}, status=200)


@csrf_exempt
@require_POST
def logout_view(request):
    try:
        if request.content_type and request.content_type.startswith('application/json'):
            payload = json.loads(request.body.decode() or '{}')
            refresh_token = payload.get('refresh')
        else:
            refresh_token = request.POST.get('refresh')
    except Exception:
        return HttpResponseBadRequest('Invalid request body')

    if not refresh_token:
        return HttpResponseBadRequest('Refresh token is required')

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        return JsonResponse({'error': 'Invalid or expired refresh token'}, status=400)

    return JsonResponse({'detail': 'Logout successful'}, status=200)


@csrf_exempt
@require_POST
def logout_all(request):
    user = None
    try:
        user = getattr(request, 'user', None)
    except Exception:
        user = None

    if not user or not getattr(user, 'is_authenticated', False):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    tokens = OutstandingToken.objects.filter(user_id=user.pk)
    count = 0
    for t in tokens:
        try:
            BlacklistedToken.objects.get_or_create(token=t)
            count += 1
        except Exception:
            pass
    return None

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Return the authenticated user's basic info."""
    user = request.user
    data = {
        'id': user.pk,
        'email': getattr(user, 'email', ''),
        'username': getattr(user, 'username', None),
        'first_name': getattr(user, 'first_name', ''),
        'last_name': getattr(user, 'last_name', ''),
    }
    return Response(data)
