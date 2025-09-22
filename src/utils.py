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
        if (page_type == "clients"):
            per_page = 10
        else:
            per_page = 14
    elif 1000 <= height <= 1200:
        if (page_type == "clients"):
            per_page = 8
        else:
            per_page = 12
    elif 800 <= height < 1000:
        if (page_type == "clients"):
            per_page = 4
        else:
            per_page = 6
    elif 600 <= height < 800:
        if (page_type == "clients"):
            per_page = 3
        else:
            per_page = 5
    else:  # height < 600
        if (page_type == "clients"):
            per_page = 2
        else:
            per_page = 4

    return per_page

def get_colors(color_theme: str) -> dict:
    if color_theme == "emerald-400":
        return {
            # table rows
            "table_row_hover_color_as_tailwind_class": "emerald-200",
            "table_row_hover_color_as_oklch": "oklch(90.5% 0.093 164.15)",
            "table_row_hover_color_as_rgb": "rgb(167,243,208)",
            # table icons
            "table_icon_hover_color_as_tailwind_class": "emerald-600",
            "table_icon_hover_color_as_oklch": "oklch(59.6% 0.145 163.225)",
            # close form icons
            "close_icon_hover_color_as_tailwind_class": "emerald-400",
            "close_icon_hover_color_as_oklch": "oklch(76.5% 0.177 163.223)"
        }
    elif color_theme == "blue-400":
        return {
            # table rows
            "table_row_hover_color_as_tailwind_class": "blue-200",
            "table_row_hover_color_as_oklch": "oklch(88.2% 0.059 254.128)",
            "table_row_hover_color_as_rgb": "rgb(191,219,254)",
            # table icons
            "table_icon_hover_color_as_tailwind_class": "blue-600",
            "table_icon_hover_color_as_oklch": "oklch(54.6% 0.245 262.881)",
            # close form icons
            "close_icon_hover_color_as_tailwind_class": "blue-400",
            "close_icon_hover_color_as_oklch": "oklch(70.7% 0.165 254.624)"
        }
    elif color_theme == "violet-400":
        return {
            # table rows
            "table_row_hover_color_as_tailwind_class": "violet-200",
            "table_row_hover_color_as_oklch": "oklch(89.4% 0.057 293.283)",
            "table_row_hover_color_as_rgb": "rgb(221,214,254)",
            # table icons
            "table_icon_hover_color_as_tailwind_class": "violet-600",
            "table_icon_hover_color_as_oklch": "oklch(54.1% 0.281 293.009)",
            # close form icons
            "close_icon_hover_color_as_tailwind_class": "violet-400",
            "close_icon_hover_color_as_oklch": "oklch(70.2% 0.183 293.541)"
        }
    elif color_theme == "fuchsia-400":
        return {
            # table rows
            "table_row_hover_color_as_tailwind_class": "fuchsia-200",
            "table_row_hover_color_as_oklch": "oklch(90.3% 0.076 319.62)",
            "table_row_hover_color_as_rgb": "rgb(245,208,254)",
            # table icons
            "table_icon_hover_color_as_tailwind_class": "fuchsia-600",
            "table_icon_hover_color_as_oklch": "oklch(59.1% 0.293 322.896)",
            # close form icons
            "close_icon_hover_color_as_tailwind_class": "fuchsia-400",
            "close_icon_hover_color_as_oklch": "oklch(74% 0.238 322.16)"
        }
    elif color_theme == "rose-400":
        return {
            # table rows
            "table_row_hover_color_as_tailwind_class": "rose-200",
            "table_row_hover_color_as_oklch": "oklch(89.2% 0.058 10.001)",
            "table_row_hover_color_as_rgb": "rgb(254,205,211)",
            # table icons
            "table_icon_hover_color_as_tailwind_class": "rose-600",
            "table_icon_hover_color_as_oklch": "oklch(58.6% 0.253 17.585)",
            # close form icons
            "close_icon_hover_color_as_tailwind_class": "rose-400",
            "close_icon_hover_color_as_oklch": "oklch(71.2% 0.194 13.428)"
        }