from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.user import User
from app.repositories.question_repository import QuestionRepository
from app.repositories.quiz_repository import QuizRepository
from app.schemas.question import QuestionCreate, QuestionRead, QuestionUpdate


class QuestionService:
    def __init__(self, db: Session) -> None:
        self.quiz_repo = QuizRepository(db)
        self.repo = QuestionRepository(db)

    def _get_quiz(self, quiz_id: int) -> Quiz:
        quiz = self.quiz_repo.get(quiz_id)
        if quiz is None:
            raise NotFoundError(f"Тест табылмады: id={quiz_id}")
        return quiz

    def _get_own_quiz(self, quiz_id: int, user: User) -> Quiz:
        quiz = self._get_quiz(quiz_id)
        if quiz.owner_id != user.id and user.role != "admin":
            raise ForbiddenError("Бұл тест сіздікі емес")
        return quiz

    def _get(self, question_id: int) -> Question:
        question = self.repo.get(question_id)
        if question is None:
            raise NotFoundError(f"Сұрақ табылмады: id={question_id}")
        return question

    def _get_own(self, question_id: int, user: User) -> tuple[Question, Quiz]:
        question = self._get(question_id)
        quiz = self._get_own_quiz(question.quiz_id, user)
        return question, quiz

    @staticmethod
    def _validate_question_rules(
        quiz: Quiz,
        options: list[str],
        correct_option: int,
    ) -> None:
        if quiz.status == "published":
            raise BadRequestError("Жарияланған тесттің сұрақтарын өзгертуге болмайды")
        if len(options) != 4:
            raise BadRequestError("Сұрақта дәл 4 жауап нұсқасы болуы керек")
        cleaned = [opt.strip() for opt in options if opt.strip()]
        if len(set(cleaned)) != 4:
            raise BadRequestError("Жауап нұсқалары бос болмауы және қайталанбауы керек")
        if correct_option < 0 or correct_option >= len(options):
            raise BadRequestError("Дұрыс жауап индексі жауап нұсқаларына сәйкес емес")

    def create_question(
        self,
        quiz_id: int,
        data: QuestionCreate,
        user: User,
    ) -> QuestionRead:
        quiz = self._get_own_quiz(quiz_id, user)
        self._validate_question_rules(quiz, data.options, data.correct_option)
        question = Question(
            quiz_id=quiz.id,
            question_text=data.question_text,
            options=data.options,
            correct_option=data.correct_option,
        )
        return QuestionRead.model_validate(self.repo.create(question))

    def update_question(
        self,
        question_id: int,
        data: QuestionUpdate,
        user: User,
    ) -> QuestionRead:
        question, quiz = self._get_own(question_id, user)
        changes = data.model_dump(exclude_unset=True, exclude_none=True)
        new_options = changes.get("options", question.options)
        new_correct = changes.get("correct_option", question.correct_option)
        self._validate_question_rules(quiz, new_options, new_correct)
        for field, value in changes.items():
            setattr(question, field, value)
        return QuestionRead.model_validate(self.repo.save(question))

    def delete_question(self, question_id: int, user: User) -> None:
        question, quiz = self._get_own(question_id, user)
        if quiz.status == "published":
            raise BadRequestError("Жарияланған тесттің сұрақтарын өшіруге болмайды")
        self.repo.delete(question)
