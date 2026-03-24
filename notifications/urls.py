from django.urls import path
from . import views  # <- un solo punto, no dos

urlpatterns = [
    path(
        "",
        views.NotificationListView.as_view(),
        name="notification-list"
    ),
    path(
        "<int:notification_id>/read/",
        views.mark_as_read,
        name="notification-read"
    ),
]