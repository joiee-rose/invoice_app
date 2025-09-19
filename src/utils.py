import ctypes

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

def get_per_page():
    user32 = ctypes.windll.user32
    height = user32.GetSystemMetrics(1)

    if height > 1200:
        per_page = 14
    elif 1000 <= height <= 1200:
        per_page = 12
    elif 800 <= height < 1000:
        per_page = 8
    elif 600 <= height < 800:
        per_page = 6
    else:  # height < 600
        per_page = 4

    return per_page