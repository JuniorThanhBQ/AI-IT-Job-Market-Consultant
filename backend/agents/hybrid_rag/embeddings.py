import uuid
from typing import Any

from app.modules.consultee_profile import repository as profile_repo
from sqlmodel import Session


def build_user_profile(db: Session, user_id: uuid.UUID) -> dict | None:
    profile = profile_repo.get_profile_by_user_id(session=db, user_id=user_id)
    if not profile:
        return None

    profile_dict: dict[str, Any] = {
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "biography": profile.biography,
        "goal": profile.goal,
    }

    if profile.cv:
        cv = profile.cv
        profile_dict.update(
            {
                "job_position": cv.job_position,
                "summary": cv.summary,
                "education": cv.education,
                "skills": cv.skills or [],
                "certifications": cv.certifications or [],
                "projects": [
                    {
                        "name": p.name,
                        "role": p.role,
                        "tech_stacks": p.tech_stacks or [],
                        "description": p.description,
                    }
                    for p in (cv.projects or [])[:3]
                ],
            }
        )

    return profile_dict
