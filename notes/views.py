from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Note
from .serializers import NoteSerializer

class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['category']
    filter_backends = (SearchFilter, OrderingFilter)

    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        return Note.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def count(self, request):
        qs = self.get_queryset()
        return Response({'count': qs.count()})

    @action(detail=False, methods=['get'], url_path='counts-by-category')
    def counts_by_category(self, request):
        qs = self.get_queryset()
        grouped = qs.values('category').annotate(total=Count('id')).order_by('-total')
        result = {item['category']: item['total'] for item in grouped}
        return Response(result)
