from fastapi import HTTPException, status

def call_service_or_500(service_func, *args, **kwargs):
    success, result = service_func(*args, **kwargs)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result
        )
    return result

async def call_async_service_or_500(service_func, *args, **kwargs):
    success, result = await service_func(*args, **kwargs)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result
        )
    return result

def call_service_or_422(service_func, *args, **kwargs):
    success, result = service_func(*args, **kwargs)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=result
        )
    return result

def call_service_or_404(service_func, *args, **kwargs):
    success, result = service_func(*args, **kwargs)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result
        )
    return result