from collections.abc import Callable

from fastapi.testclient import TestClient

SAMPLE_TEXT = (
    "Қазақстан тарихы мен географиясы бойынша сабақ мәтіні. "
    "Бұл мәтіннің ұзындығы екі жүз таңбадан кем болмауы тиіс, сондықтан "
    "мұғалім оқушылардың білімін тексеру үшін негізгі ұғымдарды, даталарды "
    "және қорытынды ойларды толық енгізеді."
)


def test_quiz_crud_and_ownership_protection(
    client: TestClient,
    make_token: Callable[..., str],
) -> None:
    teacher1_token = make_token(
        sub="kc-t1",
        email="teacher1@demo.kz",
        roles=["teacher"],
    )
    teacher2_token = make_token(
        sub="kc-t2",
        email="teacher2@demo.kz",
        roles=["teacher"],
    )
    student_token = make_token(
        sub="kc-s1",
        email="student1@demo.kz",
        roles=["student"],
    )

    # Student cannot create quiz -> 403
    r_student_create = client.post(
        "/api/quizzes",
        json={"title": "Тарих тесті", "source_text": SAMPLE_TEXT},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert r_student_create.status_code == 403

    # Teacher 1 creates quiz -> 201
    r_create = client.post(
        "/api/quizzes",
        json={"title": "Тарих тесті", "source_text": SAMPLE_TEXT},
        headers={"Authorization": f"Bearer {teacher1_token}"},
    )
    assert r_create.status_code == 201
    quiz_id = r_create.json()["id"]
    assert r_create.json()["status"] == "draft"

    # Teacher 2 cannot modify Teacher 1's quiz -> 403
    r_forbidden_patch = client.patch(
        f"/api/quizzes/{quiz_id}",
        json={"title": "Бөтен өзгеріс"},
        headers={"Authorization": f"Bearer {teacher2_token}"},
    )
    assert r_forbidden_patch.status_code == 403

    # Teacher 1 updates own quiz -> 200
    r_patch = client.patch(
        f"/api/quizzes/{quiz_id}",
        json={"title": "Жаңартылған Тарих тесті"},
        headers={"Authorization": f"Bearer {teacher1_token}"},
    )
    assert r_patch.status_code == 200
    assert r_patch.json()["title"] == "Жаңартылған Тарих тесті"

    # Non-existent quiz -> 404
    r_404 = client.get("/api/quizzes/99999")
    assert r_404.status_code == 404


def test_questions_and_submissions_flow(
    client: TestClient,
    make_token: Callable[..., str],
) -> None:
    teacher_token = make_token(
        sub="kc-teacher-flow",
        email="tflow@demo.kz",
        roles=["teacher"],
    )
    other_teacher_token = make_token(
        sub="kc-teacher-other",
        email="tother@demo.kz",
        roles=["teacher"],
    )
    student_token = make_token(
        sub="kc-student-flow",
        email="sflow@demo.kz",
        roles=["student"],
    )

    # 1. Create quiz (draft)
    r_quiz = client.post(
        "/api/quizzes",
        json={"title": "Информатика сабағы", "source_text": SAMPLE_TEXT},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert r_quiz.status_code == 201
    quiz_id = r_quiz.json()["id"]

    # 2. Other teacher cannot add question to this quiz -> 403
    r_q_forbidden = client.post(
        f"/api/quizzes/{quiz_id}/questions",
        json={
            "question_text": "Python тілінің авторы кім?",
            "options": ["Гвидо ван Россум", "Бьерн Страуструп", "Джеймс Гослинг", "Деннис Ритчи"],
            "correct_option": 0,
        },
        headers={"Authorization": f"Bearer {other_teacher_token}"},
    )
    assert r_q_forbidden.status_code == 403

    # 3. Business rule: duplicate options in question -> 400 BadRequestError
    r_q_bad = client.post(
        f"/api/quizzes/{quiz_id}/questions",
        json={
            "question_text": "Қате нұсқалары бар сұрақ?",
            "options": ["Бірдей", "Бірдей", "Үшінші", "Төртінші"],
            "correct_option": 0,
        },
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert r_q_bad.status_code == 400

    # 4. Owner adds valid question -> 201
    r_q_create = client.post(
        f"/api/quizzes/{quiz_id}/questions",
        json={
            "question_text": "Python тілінің авторы кім?",
            "options": ["Гвидо ван Россум", "Бьерн Страуструп", "Джеймс Гослинг", "Деннис Ритчи"],
            "correct_option": 0,
        },
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert r_q_create.status_code == 201
    question_id = r_q_create.json()["id"]

    # 5. Owner updates question -> 200
    r_q_patch = client.patch(
        f"/api/questions/{question_id}",
        json={"correct_option": 1},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert r_q_patch.status_code == 200
    assert r_q_patch.json()["correct_option"] == 1

    # 6. Student cannot submit to a draft quiz -> 400 BadRequestError
    r_sub_draft = client.post(
        f"/api/quizzes/{quiz_id}/submissions",
        json={"answers": [1]},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert r_sub_draft.status_code == 400

    # 7. Teacher publishes quiz -> 200
    r_pub = client.patch(
        f"/api/quizzes/{quiz_id}",
        json={"status": "published"},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert r_pub.status_code == 200

    # 8. Business rule: cannot edit question after quiz is published -> 400
    r_q_after_pub = client.patch(
        f"/api/questions/{question_id}",
        json={"correct_option": 0},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert r_q_after_pub.status_code == 400

    # 9. Student submits answers to published quiz -> 201
    r_sub = client.post(
        f"/api/quizzes/{quiz_id}/submissions",
        json={"answers": [1]},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert r_sub.status_code == 201
    assert r_sub.json()["score"] == 1

    # 10. Repeat submission by same student -> 409 Conflict
    r_sub_dup = client.post(
        f"/api/quizzes/{quiz_id}/submissions",
        json={"answers": [1]},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert r_sub_dup.status_code == 409

    # 11. Student views own submissions via GET /api/submissions/me -> 200
    r_me = client.get(
        "/api/submissions/me",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert r_me.status_code == 200
    assert len(r_me.json()) == 1
    assert r_me.json()[0]["score"] == 1
