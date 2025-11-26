from rest_framework import viewsets, pagination
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Note
from .serializers import NoteSerializer


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'total_notes': self.page.paginator.count,
            'num_pages': self.page.paginator.num_pages,
            'page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'results': data,
        })


class NoteViewSet(viewsets.ModelViewSet):
    """ModelViewSet for Note. Users only see and create their own notes."""
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        return Note.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def count(self, request):
        qs = self.get_queryset()
        return Response({'count': qs.count()})
