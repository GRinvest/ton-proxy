from fastapi import APIRouter
from fastapi.responses import UJSONResponse
from pydantic import BaseModel

router = APIRouter()


class Submit(BaseModel):
    solution: str


@router.post("/submit")
async def set_submit(submit: Submit):
    data = submit.dict()
    print(data)
    return UJSONResponse(content={'ok': True}, headers={"Access-Control-Allow-Origin": "*"})
