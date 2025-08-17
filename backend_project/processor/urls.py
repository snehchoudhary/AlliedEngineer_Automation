from django.urls import path
from .views import ProcessFileAPIView

urlpatterns = [
    # POST /api/process/<processor_key>/
    path("process/<str:processor_key>/", ProcessFileAPIView.as_view(), name="process_file"),
]