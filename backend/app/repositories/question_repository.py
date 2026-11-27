from builtins import list as ListType

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.question import Question


class QuestionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_quiz(self, quiz_id: int) -> ListType[Question]:
        stmt = select(Question).where(Question.quiz_id == quiz_id).order_by(Question.id)
        return ListType(self.db.scalars(stmt).all())

    def get(self, question_id: int) -> Question | None:
        return self.db.get(Question, question_id)

    def create(self, question: Question) -> Question:
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def save(self, question: Question) -> Question:
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def delete(self, question: Question) -> None:
        self.db.delete(question)
        self.db.commit()
