from fastapi import APIRouter, Response, Request, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_csrf_protect import CsrfProtect
from starlette.status import HTTP_201_CREATED
from typing import List
from auth_utils import AuthJwtCsrf
from schemas import Todo, TodoBody, SuccessMsg
from database import db_create_todo, db_get_todos, db_get_single_todo, db_update_todo, db_delete_todo
import logging
import sys


router = APIRouter()
auth = AuthJwtCsrf()
logger = logging.getLogger('logger')


@router.post('/api/todo', response_model=Todo)
async def create_todo(
    request: Request, 
    response: Response, 
    data: TodoBody, 
    csrf_protect: CsrfProtect = Depends()
):
    logger.info(f'start: {sys._getframe().f_code.co_name}')
    new_token = auth.verify_csrf_update_jwt(request, csrf_protect=csrf_protect, headers=request.headers)
    todo = jsonable_encoder(data)
    res = await db_create_todo(todo)
    response.status_code = HTTP_201_CREATED
    response.set_cookie(
        key='access_key',
        value=f'Bearer {new_token}',
        httponly=True,
        samesite='none',
        secure=True
    )
    if not res:
        raise HTTPException(404, detail='create task failed')
    else:
        return res


@router.get('/api/todo', response_model=List[Todo])
async def get_todos(request: Request):
    logger.info(f'start: {sys._getframe().f_code.co_name}')
    # auth.verify_jwt(request)
    res = await db_get_todos()
    return res


@router.get('/api/todo/{id}', response_model=Todo)
async def get_single_todo(request: Request, response: Response, id: str):
    logger.info(f'start: {sys._getframe().f_code.co_name}')
    new_token, _ = auth.verify_update_jwt(request)
    response.set_cookie(
        key='access_key',
        value=f'Bearer {new_token}',
        httponly=True,
        samesite='none',
        secure=True
    )
    res = await db_get_single_todo(id)
    if not res:
        return HTTPException(
            status_code=404,
            detail=f"Task of ID:{id} doesn't exist"
        )
    else:
        return res


@router.put('/api/todo/{id}', response_model=Todo)
async def update_todo(
    request: Request, 
    response: Response,
    id: str, 
    data: TodoBody,
    csrf_protect: CsrfProtect = Depends()
):
    logger.info(f'start: {sys._getframe().f_code.co_name}')
    new_token = auth.verify_csrf_update_jwt(request, csrf_protect=csrf_protect, headers=request.headers)
    todo = jsonable_encoder(data)
    res = await db_update_todo(id, data=todo)
    response.set_cookie(
        key='access_key',
        value=f'Bearer {new_token}',
        httponly=True,
        samesite='none',
        secure=True
    )
    if res:
        return res
    else:
        raise HTTPException(
            status_code=404,
            detail='Update task failed'
        )
    

@router.delete('/api/todo/{id}', response_model=SuccessMsg)
async def delete_todo(
    request: Request, 
    response: Response,
    id: str,
    csrf_protect: CsrfProtect = Depends()
):
    logger.info(f'start: {sys._getframe().f_code.co_name}')
    new_token = auth.verify_csrf_update_jwt(request, csrf_protect=csrf_protect, headers=request.headers)
    res = await db_delete_todo(id)
    response.set_cookie(
        key='access_key',
        value=f'Bearer {new_token}',
        httponly=True,
        samesite='none',
        secure=True
    )
    if res:
        return {'message': 'Successfully deleted'}
    else:
        raise HTTPException(
            status_code=404,
            detail='Delete task failed'
        )