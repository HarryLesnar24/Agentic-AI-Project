from __future__ import annotations

from typing import Any, TypedDict, Annotated
from dataclasses import dataclass, field, asdict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


@dataclass
class Topic:
    title: str
    description: str
    estimated_minutes: int
    prerequisites: list[str] = field(default_factory=list)
    status: str = "pending"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Topic":
        return cls(
            title=data['title'],
            description=data['description'],
            estimated_minutes=data['estimated_minutes'],
            prerequisites=data.get("prerequisites", []),
            status=data.get("status", "pending")
        )
    

@dataclass
class StudyRoadMap:
    goal: str
    total_weeks: int
    topics: list[Topic]
    weekly_hours: int = 5

    def to_dict(self):
        return {
            "goal": self.goal,
            "total_weeks": self.total_weeks,
            "weekly_hours": self.weekly_hours,
            "topics": [t.to_dict() for t in self.topics]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "StudyRoadMap":
        return cls(
            goal=data["goal"],
            total_weeks=data["total_weeks"],
            weekly_hours=data.get("weekly_hours", 5),
            topics=[Topic.from_dict(t) for t in data.get("topics", [])]
        )
    
    def completed_count(self) -> int:
        return sum(1 for t in self.topics if t.status == "completed")

    def is_complete(self) -> bool:
        return all(t.status in ("completed", "needs_review") for t in self.topics)

@dataclass
class QuizQuestion:
    question: str
    expected_answer: str
    user_answer: str = ""
    correct: bool = False
    feedback: str = ""
    score: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)
    
@dataclass
class QuizResult:
    topic: str
    questions: list
    score: float
    weak_areas: list[str]
    timestamp: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "QuizResult":
        return cls(
            topic=data.get("topic", ""),
            questions=[],
            score=float(data.get("score", 0.0)),
            weak_areas=data.get("weak_areas", []),
            timestamp=data.get("timestamp", "")
        )

    def passed(self) -> bool:
        return self.score >= 0.5
    
    def strong_passed(self) -> bool:
        return self.score >= 0.75
    

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    session_id: str
    goal: str
    roadmap: StudyRoadMap | None
    approved: bool
    current_topic_index: int
    quiz_results: list[QuizResult]
    weak_areas: list[str]
    study_materials_path: str
    error: str | None
    
def initial_state(
        goal: str,
        session_id: str,
        study_materials_path: str = "study_materials/sample_notes",
) -> dict:

    return {
        "messages": [],
        "session_id": session_id,
        "goal": goal,
        "roadmap": None,
        "approved": False,
        "current_topic_index": 0,
        "quiz_results": [],
        "weak_areas": [],
        "study_materials_path": study_materials_path,
        "error": None
        
    }

def get_current_topic(state: dict) -> Topic | None:
    roadmap = state.get("roadmap")
    if roadmap is None:
        return None
    if isinstance(roadmap, dict):
        topics_raw = roadmap.get("topics", [])
    else:
        topics_raw = roadmap.topics

    idx = state.get("current_topic_index", 0)
    if idx >= len(topics_raw):
        return None
    t = topics_raw[idx]
    if isinstance(t, dict):
        return Topic.from_dict(t)
    return t

def get_latest_quiz_result(state: dict) -> QuizResult | None:
    results = state.get("quiz_results", [])
    if not results:
        return None
    latest = results[-1]

    if isinstance(latest, dict):
        return QuizResult.from_dict(latest)

    return latest

def session_is_complete(state: dict) -> bool:
    roadmap = state.get("roadmap")
    if roadmap is None:
        return True
    topics = roadmap.get("topics", []) if isinstance(roadmap, dict) else roadmap.topics
    idx = state.get("current_topic_index", 0)
    return idx >= len(topics)
    