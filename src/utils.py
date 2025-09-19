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

def get_per_page(page_type: str) -> int:
    user32 = ctypes.windll.user32
    height = user32.GetSystemMetrics(1)

    if height > 1200:
        if (page_type == "clients" or
            page_type == "invoices" or
            page_type == "quotes"
        ):
            per_page = 10
        elif (page_type == "services"):
            per_page = 14
    elif 1000 <= height <= 1200:
        if (page_type == "clients" or
            page_type == "invoices" or
            page_type == "quotes"
        ):
            per_page = 8
        elif (page_type == "services"):
            per_page = 12
    elif 800 <= height < 1000:
        if (page_type == "clients" or
            page_type == "invoices" or
            page_type == "quotes"
        ):
            per_page = 4
        elif (page_type == "services"):
            per_page = 8
    elif 600 <= height < 800:
        if (page_type == "clients" or
            page_type == "invoices" or
            page_type == "quotes"
        ):
            per_page = 2
        elif (page_type == "services"):
            per_page = 6
    else:  # height < 600
        if (page_type == "clients" or
            page_type == "invoices" or
            page_type == "quotes"
        ):
            per_page = 1
        elif (page_type == "services"):
            per_page = 4

    return per_page