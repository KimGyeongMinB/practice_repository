from django.urls import path
from .views import InquiryListAPIView, InquiryRetrieveUpdateDestroyAPIView, InquiryRestoration

app_name = 'inquires'

urlpatterns = [
    path("list/", InquiryListAPIView.as_view(), name="inquiry_list"),
    path("list/<int:pk>/", InquiryRetrieveUpdateDestroyAPIView.as_view(), name="retrieve_update_delete"),
    path("restore-list/", InquiryRestoration.as_view(), name='restore_list'),
    path("restore/<int:pk>/", InquiryRestoration.as_view(), name='restore')
]