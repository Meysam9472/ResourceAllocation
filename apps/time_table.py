from fastapi import APIRouter

router = APIRouter()


@router.get("time-table-maker")
async def time_table_maker():
    ...