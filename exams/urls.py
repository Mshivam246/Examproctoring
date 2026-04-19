from django.urls import path

from . import views

urlpatterns = [
    path("", views.exam_list, name="exam_list"),
    path("exam/<int:exam_id>/", views.take_exam, name="take_exam"),
    path("exam/<int:exam_id>/submit/", views.submit_exam, name="submit_exam"),
    path("exam/<int:exam_id>/result/", views.exam_result, name="exam_result"),
    path("api/proctor/event/", views.proctor_event_api, name="proctor_event_api"),
]
