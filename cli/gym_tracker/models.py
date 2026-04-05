from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    muscle_group = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    sleep_hours = Column(Float, nullable=True)
    tags = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    photo_path = Column(String, nullable=True)
    blocks = relationship("Block", back_populates="workout", order_by="Block.order")


class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    scheme = Column(Text, nullable=True)
    workout = relationship("Workout", back_populates="blocks")
    sets = relationship("Set", back_populates="block", order_by="Set.round")


class Set(Base):
    __tablename__ = "sets"

    id = Column(Integer, primary_key=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    round = Column(Integer, nullable=False)
    weight_lbs = Column(Float, nullable=True)
    reps = Column(Integer, nullable=True)
    rpe = Column(Float, nullable=True)
    duration_secs = Column(Integer, nullable=True)
    distance_m = Column(Float, nullable=True)
    calories = Column(Float, nullable=True)
    watts = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    block = relationship("Block", back_populates="sets")
    exercise = relationship("Exercise")


class ExerciseRelation(Base):
    __tablename__ = "exercise_relations"

    exercise_id = Column(Integer, ForeignKey("exercises.id"), primary_key=True)
    related_exercise_id = Column(Integer, ForeignKey("exercises.id"), primary_key=True)
    relation_type = Column(String, nullable=False, default="variant")
