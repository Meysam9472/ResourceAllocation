from fastapi import APIRouter

router = APIRouter()


@router.get('/get-all-users')
async def get_all_users():
    pass
