from typing import List

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase
from app.models.domains import Course, CourseLecturer, CourseStudent
from app.models.schemas import CourseStudentsUpdate, CourseLecturersUpdate
from app.models.schemas.course import CourseCreate, CourseUpdate
from app.resources import strings


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    def get_course_lecturers(self, db: Session, *, course_id: int, semester_id: int) -> CourseLecturer:
        return db.query(CourseLecturer).filter(
            CourseLecturer.semester_id == semester_id,
            CourseLecturer.course_id == course_id
        ).all()

    def get_course_students(self, db: Session, *, course_id: int, semester_id: int) -> CourseStudent:
        return db.query(CourseStudent).filter(
            CourseStudent.semester_id == semester_id,
            CourseStudent.course_id == course_id
        ).all()

    def create(self, db: Session, *, obj_in: CourseCreate):
        course_dict = jsonable_encoder(obj_in.copy(exclude={"lecturers", "students"}))
        try:
            new_course = Course(**course_dict)
            db.add(new_course)
            db.commit()
            db.refresh(new_course)

            current_semester = crud.semester.get_active_semester(db)
            list_lecturers = jsonable_encoder(obj_in.lecturers)
            for lecturer_id in list_lecturers:
                lecturer = crud.lecturer.get(db, id=lecturer_id)
                if lecturer:
                    course_lecturer = CourseLecturer(
                        semester_id=current_semester.id,
                        course_id=new_course.id,
                        lecturer_id=lecturer.id
                    )
                    db.add(course_lecturer)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=strings.ERROR_MODEL_ID_NOT_EXIST.format(strings.MODEL_LECTURER, lecturer_id)
                    )

            list_students = jsonable_encoder(obj_in.students)
            for student_id in list_students:
                student = crud.student.get(db, id=student_id)
                if student:
                    course_student = CourseStudent(
                        semester_id=current_semester.id,
                        course_id=new_course.id,
                        student_id=student.id
                    )
                    db.add(course_student)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=strings.ERROR_MODEL_ID_NOT_EXIST.format(strings.MODEL_STUDENT, student_id)
                    )
            db.commit()
        except SQLAlchemyError as e:
            print(e.args)
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=strings.ERROR_INTERNAL_SERVER_ERROR)
        return new_course

    def add_course_lecturers(self, db: Session, *, course_id: int, obj_in: CourseLecturersUpdate) -> None:
        try:
            current_semester = crud.semester.get_active_semester(db)
            for lecturer_id in obj_in.lecturers:
                lecturer = crud.lecturer.get(db, id=lecturer_id)
                if lecturer:
                    course_lecturer = CourseLecturer(
                        semester_id=current_semester.id,
                        course_id=course_id,
                        lecturer_id=lecturer.id
                    )
                    db.add(course_lecturer)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=strings.ERROR_MODEL_ID_NOT_EXIST.format(strings.MODEL_STUDENT, lecturer_id)
                    )
            db.commit()
        except SQLAlchemyError as e:
            print(e.args)
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=strings.ERROR_INTERNAL_SERVER_ERROR)

    def add_course_students(self, db: Session, *, course_id: int, obj_in: CourseStudentsUpdate) -> None:
        try:
            current_semester = crud.semester.get_active_semester(db)
            for student_id in obj_in.students:
                student = crud.student.get(db, id=student_id)
                if student:
                    course_student = CourseStudent(
                        semester_id=current_semester.id,
                        course_id=course_id,
                        student_id=student.id
                    )
                    db.add(course_student)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=strings.ERROR_MODEL_ID_NOT_EXIST.format(strings.MODEL_STUDENT, student_id)
                    )
            db.commit()
        except SQLAlchemyError as e:
            print(e.args)
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=strings.ERROR_INTERNAL_SERVER_ERROR)

    def delete_course_lecturers(self, db: Session, *, course_id: int, obj_in: CourseLecturersUpdate) -> None:
        try:
            current_semester = crud.semester.get_active_semester(db)
            for lecturer_id in obj_in.lecturers:
                lecturer = crud.lecturer.get(db, id=lecturer_id)
                if lecturer:
                    course_lecturer = db.query(CourseLecturer).filter_by(
                        semester_id=current_semester.id,
                        course_id=course_id,
                        lecturer_id=lecturer.id
                    ).first()
                    # CourseLecturer(
                    #     semester_id=current_semester.id,
                    #     course_id=course_id,
                    #     lecturer_id=lecturer.id
                    # )
                    db.delete(course_lecturer)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=strings.ERROR_MODEL_ID_NOT_EXIST.format(strings.MODEL_STUDENT, lecturer_id)
                    )
            db.commit()
        except SQLAlchemyError as e:
            print(e.args)
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=strings.ERROR_INTERNAL_SERVER_ERROR)

    def delete_course_students(self, db: Session, *, course_id: int, obj_in: CourseStudentsUpdate) -> None:
        try:
            current_semester = crud.semester.get_active_semester(db)
            for student_id in obj_in.students:
                student = crud.student.get(db, id=student_id)
                if student:
                    course_student = db.query(CourseStudent).filter_by(
                        semester_id=current_semester.id,
                        course_id=course_id,
                        student_id=student.id
                    ).first()
                    db.delete(course_student)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=strings.ERROR_MODEL_ID_NOT_EXIST.format(strings.MODEL_STUDENT, student_id)
                    )
            db.commit()
        except SQLAlchemyError as e:
            print(e.args)
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=strings.ERROR_INTERNAL_SERVER_ERROR)


course = CRUDCourse(Course)
