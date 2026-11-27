from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from app.models.submission import Submission
from app.models.user import User
from app.repositories.question_repository import QuestionRepository
from app.repositories.quiz_repository import QuizRepository
from app.repositories.submission_repository import SubmissionRepository
from app.schemas.submission import SubmissionCreate, SubmissionRead


class SubmissionService:
    def __init__(self, db: Session) -> None:
        self.quiz_repo = QuizRepository(db)
        self.question_repo = QuestionRepository(db)
        self.repo = SubmissionRepository(db)

    def submit_quiz(
        self,
        quiz_id: int,
        data: SubmissionCreate,
        user: User,
    ) -> SubmissionRead:
        quiz = self.quiz_repo.get(quiz_id)
        if quiz is None:
            raise NotFoundError(f"Тест табылмады: id={quiz_id}")
        if quiz.status != "published":
            raise BadRequestError("Тек жарияланған (published) тестті тапсыруға болады")
        if not data.answers:
            raise BadRequestError("Жауаптар бос болмауы керек")

        existing = self.repo.get_by_quiz_and_student(quiz_id, user.id)
        if existing is not None:
            raise ConflictError("Сіз бұл тестті бұрын тапсырғансыз")

        questions = self.question_repo.list_by_quiz(quiz_id)
        score = 0
        if isinstance(data.answers, dict):
            for q in questions:
                ans = data.answers.get(str(q.id))
                if ans is not None and ans == q.correct_option:
                    score += 1
        elif isinstance(data.answers, list):
            for idx, q in enumerate(questions):
                if idx < len(data.answers) and data.answers[idx] == q.correct_option:
                    score += 1

        submission = Submission(
            quiz_id=quiz_id,
            student_id=user.id,
            answers=data.answers,
            score=score,
        )
        return SubmissionRead.model_validate(self.repo.create(submission))

    def list_my_submissions(self, user: User) -> list[SubmissionRead]:
        return [
            SubmissionRead.model_validate(s)
            for s in self.repo.list_by_student(user.id)
        ]

    def list_submissions(
        self,
        user: User,
        quiz_id: int | None = None,
    ) -> list[SubmissionRead]:
        if user.role == "student":
            raise ForbiddenError("Оқушы барлық нәтижелер тізімін көре алмайды")
        if quiz_id is not None:
            rows = self.repo.list_by_quiz(quiz_id)
        else:
            rows = self.repo.list()
        return [SubmissionRead.model_validate(s) for s in rows]
