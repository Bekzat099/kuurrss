from builtins import list as ListType

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.submission import Submission


class SubmissionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> ListType[Submission]:
        stmt = select(Submission).order_by(Submission.id)
        return ListType(self.db.scalars(stmt).all())

    def list_by_student(self, student_id: int) -> ListType[Submission]:
        stmt = (
            select(Submission)
            .where(Submission.student_id == student_id)
            .order_by(Submission.id)
        )
        return ListType(self.db.scalars(stmt).all())

    def list_by_quiz(self, quiz_id: int) -> ListType[Submission]:
        stmt = (
            select(Submission)
            .where(Submission.quiz_id == quiz_id)
            .order_by(Submission.id)
        )
        return ListType(self.db.scalars(stmt).all())

    def get_by_quiz_and_student(
        self,
        quiz_id: int,
        student_id: int,
    ) -> Submission | None:
        stmt = select(Submission).where(
            Submission.quiz_id == quiz_id,
            Submission.student_id == student_id,
        )
        return self.db.scalars(stmt).first()

    def create(self, submission: Submission) -> Submission:
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission
