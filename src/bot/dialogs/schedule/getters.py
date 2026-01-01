from datetime import date, timedelta

from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from models.lesson import Lesson
from services.schedule_service import ScheduleService
from services.user_service import UserService


def format_lesson(lesson: Lesson) -> str:
    lesson_type_display = {
        "лекционного": "Лекция",
        "семинарского": "Семинар",
    }.get(lesson.lesson_type, lesson.lesson_type)

    time_str = f"{lesson.start_time:%H:%M}–{lesson.end_time:%H:%M}"

    header = f"🕒 {time_str} — <b>{lesson.subject}</b>"

    meta_parts: list[str] = [lesson_type_display]

    if lesson.room:
        meta_parts.append(f"🚪 {lesson.room}")

    if lesson.teacher:
        meta_parts.append(f"👨‍🏫 {lesson.teacher}")

    meta = " · ".join(meta_parts)

    return f"{header}\n   {meta}"


def _format_date_title(d: date, mode: str) -> str:
    """Format date display for current view."""
    if mode == "day":
        today = date.today()
        if d == today:
            return f"📅 <b>Расписание на сегодня</b> ({d.strftime('%d.%m')})"
        elif d == today + timedelta(days=1):
            return f"📅 <b>Расписание на завтра</b> ({d.strftime('%d.%m')})"
        else:
            weekday = ("пн", "вт", "ср", "чт", "пт", "сб", "вс")[d.weekday()]
            return f"📅 <b>Расписание на {d.strftime('%d.%m')}</b> ({weekday})"
    else:
        week_end = d + timedelta(days=6)
        return (
            f"📅 <b>Расписание на неделю</b> ({d.strftime('%d.%m')} — {week_end.strftime('%d.%m')})"
        )


@inject
async def get_schedule(
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
    schedule_service: FromDishka[ScheduleService],
    **_: object,
) -> dict:
    user_id = dialog_manager.middleware_data["event_from_user"].id
    user = await user_service.get_by_telegram_id(user_id)
    if not user or not user.subgroup_id:
        return {
            "schedule_text": "⚠️ Сначала выберите группу и подгруппу в разделе настроек.",
            "has_lessons": False,
        }
    subgroup_id = user.subgroup_id

    # Read state from dialog_data
    mode = dialog_manager.dialog_data.get("mode", "day")
    anchor_str = dialog_manager.dialog_data.get("anchor_date", date.today().isoformat())
    anchor = date.fromisoformat(anchor_str)

    # Fetch lessons based on mode
    if mode == "day":
        lessons = await schedule_service.get_schedule_for_date(subgroup_id, anchor)
        title = _format_date_title(anchor, "day")
    else:  # week
        lessons = await schedule_service.get_schedule_for_week(subgroup_id, anchor)
        title = _format_date_title(anchor, "week")

    if not lessons:
        return {
            "schedule_text": f"{title}\n\n📭 Занятий нет",
            "has_lessons": False,
        }

    if mode == "week":
        schedule_text = title + "\n\n"
        current_date = None
        for lesson in lessons:
            if lesson.date != current_date:
                if current_date is not None:
                    schedule_text += "\n"
                weekday = lesson.date.weekday()
                day_display = (
                    "Понедельник",
                    "Вторник",
                    "Среда",
                    "Четверг",
                    "Пятница",
                    "Суббота",
                    "Воскресенье",
                )[weekday]

                schedule_text += f"<b>{day_display} · {lesson.date:%d.%m}</b>\n"
                current_date = lesson.date

            schedule_text += format_lesson(lesson) + "\n\n"
    else:
        schedule_text = title + "\n\n"
        schedule_text += "\n\n".join(format_lesson(lesson) for lesson in lessons)

    return {
        "schedule_text": schedule_text,
        "has_lessons": True,
    }
