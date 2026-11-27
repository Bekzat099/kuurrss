from builtins import list as ListType

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.quiz import Quiz


class QuizRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> ListType[Quiz]:
        stmt = select(Quiz).order_by(Quiz.id)
        return ListType(self.db.scalars(stmt).all())

    def get(self, quiz_id: int) -> Quiz | None:
        return self.db.get(Quiz, quiz_id)

    def create(self, quiz: Quiz) -> Quiz:
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def save(self, quiz: Quiz) -> Quiz:
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def delete(self, quiz: Quiz) -> None:
        self.db.delete(quiz)
        self.db.commit()
