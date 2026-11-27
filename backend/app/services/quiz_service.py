from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.quiz import Quiz
from app.models.user import User
from app.repositories.quiz_repository import QuizRepository
from app.schemas.quiz import QuizCreate, QuizForTeacher, QuizUpdate


class QuizService:
    def __init__(self, repo: QuizRepository | Session) -> None:
        if isinstance(repo, Session):
            self.repo = QuizRepository(repo)
        else:
            self.repo = repo

    def _get(self, quiz_id: int) -> Quiz:
        quiz = self.repo.get(quiz_id)
        if quiz is None:
            raise NotFoundError(f"Тест табылмады: id={quiz_id}")
        return quiz

    def _get_own(self, quiz_id: int, user: User) -> Quiz:
        quiz = self._get(quiz_id)
        if quiz.owner_id != user.id and user.role != "admin":
            raise ForbiddenError("Бұл тест сіздікі емес")
        return quiz

    def list_quizzes(self) -> list[QuizForTeacher]:
        return [QuizForTeacher.model_validate(q) for q in self.repo.list()]

    def get_quiz(self, quiz_id: int) -> QuizForTeacher:
        quiz = self._get(quiz_id)
        return QuizForTeacher.model_validate(quiz)

    def create_quiz(self, data: QuizCreate, user: User) -> QuizForTeacher:
        if user.role not in ("teacher", "admin"):
            raise ForbiddenError("Тест құрастыруға тек мұғалімнің құқығы бар")
        quiz = Quiz(
            title=data.title,
            source_text=data.source_text,
            teacher_id=user.id,
            status="draft",
        )
        return QuizForTeacher.model_validate(self.repo.create(quiz))

    def update_quiz(self, quiz_id: int, data: QuizUpdate, user: User) -> QuizForTeacher:
        quiz = self._get_own(quiz_id, user)
        changes = data.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in changes.items():
            setattr(quiz, field, value)
        return QuizForTeacher.model_validate(self.repo.save(quiz))

    def delete_quiz(self, quiz_id: int, user: User) -> None:
        quiz = self._get_own(quiz_id, user)
        self.repo.delete(quiz)
