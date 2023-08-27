from fastapi import APIRouter

router = APIRouter(
    prefix='/gestiondigital',
    tags=['Core'] #Divisor para la documentacion
)

@router.get('/')
def test_router():
    return {"data":"This is a test"}