from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PollOptionBase(BaseModel):
    text: str

class PollOptionCreate(PollOptionBase):
    pass

class PollOption(PollOptionBase):
    id: int
    poll_id: int
    votes_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class PollBase(BaseModel):
    question: str
    expires_at: Optional[datetime] = None

class PollCreate(PollBase):
    options: List[str]

class Poll(PollBase):
    id: int
    post_id: int
    created_at: datetime
    options: List[PollOption]

    model_config = ConfigDict(from_attributes=True)

class PollVoteBase(BaseModel):
    option_id: int

class PollVoteCreate(PollVoteBase):
    pass

class PollVote(PollVoteBase):
    id: int
    poll_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
