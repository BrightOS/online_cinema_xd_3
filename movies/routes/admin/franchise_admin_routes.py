from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import queries
from schemas.franchise import FranchiseCreateRequest, FranchiseBriefResponse
from session import get_session

router = APIRouter(prefix="/admin/franchises", tags=["Franchises (Admin)"])


@router.post(
    "/",
    response_model=FranchiseBriefResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new franchise"
)
async def create_franchise(
    franchise_data: FranchiseCreateRequest,
    db: AsyncSession = Depends(get_session)
):
    db_franchise = await queries.create_franchise(db, franchise_data)
    response = FranchiseBriefResponse.model_validate(db_franchise)
    return response


@router.delete(
    "/{franchise_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a franchise and all its associated locales"
)
async def delete_franchise(
    franchise_id: int,
    db: AsyncSession = Depends(get_session)
):
    success = await queries.delete_franchise(db, franchise_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Franchise not found"
        )
    return
