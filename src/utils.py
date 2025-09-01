from fastapi import HTTPException, status

def call_service_or_500(service_func, *args, **kwargs):
    success, message, data = service_func(*args, **kwargs)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    return message, data

async def call_async_service_or_500(service_func, *args, **kwargs):
    success, message, data = await service_func(*args, **kwargs)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    return message, data

def call_service_or_422(service_func, *args, **kwargs):
    success, message, data = service_func(*args, **kwargs)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message
        )
    return message, data

def call_service_or_404(service_func, *args, **kwargs):
    success, message, data = service_func(*args, **kwargs)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )
    return message, data