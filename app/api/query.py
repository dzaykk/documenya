from fastapi import APIRouter

from app.api.dependencies import (
    CurrentUser,
    QueryServiceDep,
)
from app.ai.query.dto import QueryRequest, QueryResponse


router = APIRouter(
    prefix="/query",
    tags=["AI Query"],
)


@router.post(
    "",
    response_model=QueryResponse,
    summary="Ask question about documents",
)
async def ask_question(
    data: QueryRequest,
    current_user: CurrentUser,
    service: QueryServiceDep,
):

    return await service.ask(
        request=data.model_copy(
            update={
                "owner_id": current_user.id,
            }
        )
    )