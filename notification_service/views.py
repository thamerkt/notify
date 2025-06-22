from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Notification.objects.order_by('-created_at')
        user_param = self.request.query_params.get('user')
        if user_param:
            queryset = queryset.filter(user=user_param)
        return queryset

    @action(detail=False, methods=['post'], url_path='mark-read')
    def mark_as_read(self, request):
        user_param = request.data.get('user')
        if not user_param:
            return Response({"error": "User parameter is required"}, status=400)

        notifications = Notification.objects.filter(user=user_param, is_read=False)
        updated_count = notifications.update(is_read=True)

        return Response({"marked_as_read": updated_count})
