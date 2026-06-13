from __future__ import annotations

import json
from re import S
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

    def is_complete(self) -> bool:
        return all(t.status in ("completed", "needs_review") for t in self.topics)
    
@dataclass
class QuizResult:
    topic: str
    question: list
    score: float
    week_areas: list[str]
    timestamp: str = ""


    def passed(self) -> bool:
        return self.score >= 0.5

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
    idx = state.get("current_topic_index", 0)
    if idx >= len(roadmap.topics):
        return None
    return roadmap.topics[idx]


def session_is_complete(state: dict) -> bool:
    roadmap = state.get("roadmap")
    if roadmap is None:
        return True
    idx = state.get("current_topic_index", 0)
    return idx >= len(roadmap.topics)
    