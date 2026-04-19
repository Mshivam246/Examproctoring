import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Exam, ProctorEvent, Submission


@login_required
def exam_list(request):
    now = timezone.now()
    exams = Exam.objects.filter(is_active=True, end_time__gte=now).order_by("start_time")
    return render(request, "exams/exam_list.html", {"exams": exams, "now": now})


@login_required
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam.objects.prefetch_related("questions__choices"), id=exam_id, is_active=True)

    if Submission.objects.filter(exam=exam, user=request.user).exists():
        messages.info(request, "You already submitted this exam.")
        return redirect("exam_result", exam_id=exam.id)

    return render(request, "exams/take_exam.html", {"exam": exam})


@login_required
@require_POST
def submit_exam(request, exam_id):
    exam = get_object_or_404(Exam.objects.prefetch_related("questions__choices"), id=exam_id, is_active=True)

    if Submission.objects.filter(exam=exam, user=request.user).exists():
        return redirect("exam_result", exam_id=exam.id)

    answers = {}
    score = 0

    for question in exam.questions.all():
        choice_key = f"question_{question.id}"
        selected_choice_id = request.POST.get(choice_key)
        if selected_choice_id:
            try:
                selected_choice_id = int(selected_choice_id)
            except ValueError:
                continue
            answers[str(question.id)] = selected_choice_id

            correct_choice = question.choices.filter(is_correct=True).first()
            if correct_choice and selected_choice_id == correct_choice.id:
                score += question.marks

    Submission.objects.create(
        exam=exam,
        user=request.user,
        score=score,
        answers_json=answers,
    )

    return redirect("exam_result", exam_id=exam.id)


@login_required
def exam_result(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    submission = get_object_or_404(Submission, exam=exam, user=request.user)

    max_score = sum(question.marks for question in exam.questions.all())

    return render(
        request,
        "exams/exam_result.html",
        {
            "exam": exam,
            "submission": submission,
            "max_score": max_score,
        },
    )


@login_required
@require_POST
def proctor_event_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    exam_id = payload.get("exam_id")
    event_type = payload.get("event_type")
    severity = payload.get("severity", "medium")
    metadata = payload.get("metadata", {})

    if not exam_id or not event_type:
        return HttpResponseBadRequest("Missing exam_id or event_type")

    exam = get_object_or_404(Exam, id=exam_id)

    submission = Submission.objects.filter(exam=exam, user=request.user).first()

    ProctorEvent.objects.create(
        exam=exam,
        user=request.user,
        submission=submission,
        event_type=event_type,
        severity=severity,
        metadata=metadata if isinstance(metadata, dict) else {"raw": metadata},
    )

    return JsonResponse({"status": "ok"})
