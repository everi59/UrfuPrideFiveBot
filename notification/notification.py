from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from data.database import Database
from bot_instance import bot
from keyboards.keyboards import get_notification_keyboard
import time

scheduler = AsyncIOScheduler()
db_manager = Database()


def cancel_scheduled_notification(note_id):
    for job in scheduler.get_jobs():
        if job.id.startswith(f"deadline_{note_id}"):
            job.remove()


def schedule_notification(note_id: int, deadline_end: datetime):
    cancel_scheduled_notification(note_id=note_id)

    notifications = [
        {'delta': timedelta(days=1), 'text': '1 день'},
        {'delta': timedelta(hours=1), 'text': '1 час'},
        {'delta': timedelta(minutes=10), 'text': '10 минут'}
    ]

    note = db_manager.get_note(note_id=note_id)

    if note:
        user_id = note.user_id
        title = note.note_title
        for notification in notifications:
            notification_time = deadline_end - notification['delta']
            if notification_time > datetime.now():
                job_id = f"deadline_{note_id}_{notification['delta']}_{int(time.time())}"
                scheduler.add_job(
                    send_notification,
                    'date',
                    run_date=notification_time,
                    args=[user_id, title, note_id, notification['text']],
                    id=job_id
                )


async def send_notification(user_id: int, title: str, note_id: int, time_left: str):
    message = f"⏰ Осталось {time_left} до дедлайна <b>{title}</b>. Успейте выполнить!"
    await bot.send_message(user_id, message, reply_markup=get_notification_keyboard(note_id=note_id,
                                                                                    time_left=time_left))
