import json
from  models.models import User
from typing import List, Optional
from pathlib import Path

DB_PATH = Path("backend/user_service/app/users.json")

DB_PATH.parent.mkdir(parents=True, exist_ok=True)



def _load_users() -> List[User]:
    if not DB_PATH.exists():
        return []

    with DB_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
        return [User(**user) for user in data]

def _save_users(users: List[User]) -> None:
    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump([user.dict() for user in users], f, ensure_ascii=False, indent=4)

def get_user(email: str) -> Optional[User]:
    users = _load_users()
    for user in users:
        if user.email == email:
            return user
    return None

def set_user(user: User) -> None:
    users = _load_users()
    max_id = max((u.id for u in users if u.id is not None), default=0)
    user.id = max_id + 1
    users.append(user)
    _save_users(users)
    return user