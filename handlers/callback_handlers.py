from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from config.config import Config, load_config
from services.services import FSMContextClass, create_text_of_notes, get_note_text
from data.database import Database
from keyboards.keyboards import (get_pagination_keyboard, create_inline_kb, get_note_keyboard, create_keyboard,
                                 get_notification_keyboard)
from notification.notification import cancel_scheduled_notification, schedule_notification

router = Router()
db_manager = Database()


@router.callback_query(F.data == "add_new_note")
async def add_new_note(callback: CallbackQuery,
                       state: FSMContext):
    await state.set_state(FSMContextClass.fill_title)
    await callback.message.edit_text(text="Введите название дедлайна (от 2 до 30 символов):", reply_markup=None)


@router.callback_query(F.data == "my_notes")
async def my_notes(callback: CallbackQuery):
    user_id = callback.from_user.id

    page = 0

    notes = db_manager.get_notes_by_user_id(user_id=user_id)

    total_pages = (len(notes) + 3) // 4

    if not notes:
        await callback.answer(text="У вас пока нет ни одного дедлайна.")
        return

    result_text = create_text_of_notes(notes=notes, page=page)

    reply_markup = get_pagination_keyboard(current_page=page,
                                           total_pages=total_pages,
                                           notes=notes)

    await callback.message.edit_text(text=result_text, reply_markup=reply_markup)


@router.callback_query(F.data.startswith("page_"))
async def pagination(callback: CallbackQuery):
    user_id = callback.from_user.id

    page = int(callback.data.split('_')[1])

    notes = db_manager.get_notes_by_user_id(user_id=user_id)

    total_pages = (len(notes) + 3) // 4

    result_text = create_text_of_notes(notes=notes, page=page)

    reply_markup = get_pagination_keyboard(current_page=page,
                                           total_pages=total_pages,
                                           notes=notes)

    await callback.message.edit_text(text=result_text, reply_markup=reply_markup)


@router.callback_query(F.data.startswith("note_"))
async def note_viewing(callback: CallbackQuery):
    note_id = int(callback.data.split('_')[1])

    note = db_manager.get_note(note_id=note_id)

    if note and note.user_id == callback.from_user.id:
        pass
    else:
        await callback.answer("❌ Это не ваш дедлайн.")

    note_text = get_note_text(note)

    reply_markup = get_note_keyboard(note_id, is_done_kb=note.is_completed)

    await callback.message.edit_text(text=note_text, reply_markup=reply_markup)


@router.callback_query(F.data.startswith("edit_"))
async def edit_note(callback: CallbackQuery,
                    state: FSMContext):
    note_id = int(callback.data.split('_')[1])

    note = db_manager.get_note(note_id=note_id)

    if note and note.user_id == callback.from_user.id:
        pass
    else:
        if note:
            await callback.answer("❌ Это не ваш дедлайн.")
        else:
            await callback.answer("❌ Такого дедлайна не существует.")
        return
    if note.is_completed:
        await callback.answer("Дедлайн уже выполнен.")
        return
    
    await state.set_state(FSMContextClass.edit_title)
    await state.update_data(note_id=note_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text="Введите название дедлайна (от 2 до 30 символов):")


@router.callback_query(F.data.startswith("extend_"))
async def edit_note(callback: CallbackQuery,
                    state: FSMContext):
    note_id = int(callback.data.split('_')[1])

    note = db_manager.get_note(note_id=note_id)
    if note and note.user_id == callback.from_user.id:
        pass
    else:
        if note:
            await callback.answer("❌ Это не ваш дедлайн.")
        else:
            await callback.answer("❌ Такого дедлайна не существует.")
        return

    if note.is_completed:
        await callback.answer("Дедлайн уже выполнен.")
        return

    await state.set_state(FSMContextClass.extend_deadline)
    await state.update_data(note_id=note_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text="Введите дату окончания дедлайна:")


@router.callback_query(F.data.startswith("delete_"))
async def delete_note(callback: CallbackQuery):
    note_id = int(callback.data.split('_')[1])

    note = db_manager.get_note(note_id=note_id)

    if note and note.user_id == callback.from_user.id:
        pass
    else:
        if note:
            await callback.answer("❌ Это не ваш дедлайн.")
        else:
            await callback.answer("❌ Такого дедлайна не существует.")
        return

    user_id = callback.from_user.id

    notes_ids = db_manager.get_note_ids_by_user_id(user_id=user_id)

    page = max(0, (notes_ids.index(note_id) - 1) // 4)

    db_manager.delete_note(note_id=note_id)

    notes = db_manager.get_notes_by_user_id(user_id=user_id)

    total_pages = (len(notes) + 3) // 4

    cancel_scheduled_notification(note_id)

    if not notes:
        await callback.answer(text="У вас теперь нет дедлайнов.")
        await callback.message.edit_text(text='<b>Выбери нужное действие</b>',
                                         reply_markup=create_inline_kb(width=1,
                                                                       dct={'add_new_note': 'Добавить новый дедлайн',
                                                                            'my_notes': 'Просмотр дедлайнов'}))
        return

    result_text = create_text_of_notes(notes=notes, page=page)

    reply_markup = get_pagination_keyboard(current_page=page,
                                           total_pages=total_pages,
                                           notes=notes)

    await callback.message.edit_text(text=result_text, reply_markup=reply_markup)


@router.callback_query(F.data.startswith("back_"))
async def delete_note(callback: CallbackQuery):
    note_id = int(callback.data.split('_')[1])

    note = db_manager.get_note(note_id=note_id)

    if note and note.user_id == callback.from_user.id:
        pass
    else:
        if note:
            await callback.answer("❌ Это не ваш дедлайн.")
        else:
            await callback.answer("❌ Такого дедлайна не существует.")
        return

    user_id = callback.from_user.id

    notes = db_manager.get_notes_by_user_id(user_id=user_id)

    notes_ids = db_manager.get_note_ids_by_user_id(user_id=user_id)

    page = notes_ids.index(note_id) // 4

    total_pages = (len(notes) + 3) // 4

    result_text = create_text_of_notes(notes=notes, page=page)

    reply_markup = get_pagination_keyboard(current_page=page,
                                           total_pages=total_pages,
                                           notes=notes)

    await callback.message.edit_text(text=result_text, reply_markup=reply_markup)


@router.callback_query(F.data == "exit")
async def exit_handler(callback: CallbackQuery):
    await callback.message.edit_text(text='<b>Выбери нужное действие</b>',
                                     reply_markup=create_inline_kb(width=1,
                                                                   dct={'add_new_note': 'Добавить новый дедлайн',
                                                                        'my_notes': 'Просмотр дедлайнов'}))


@router.callback_query(F.data.startswith("done_"))
async def done(callback: CallbackQuery):
    note_id = int(callback.data.split('_')[1])

    time_left = str(callback.data.split('_')[2])

    note = db_manager.get_note(note_id=note_id)

    if note and note.user_id == callback.from_user.id:
        pass
    else:
        if note:
            await callback.answer("❌ Это не ваш дедлайн.")
        else:
            await callback.answer("❌ Такого дедлайна не существует.")
        return

    db_manager.mark_note_as_completed(note_id=note_id)
    cancel_scheduled_notification(note_id=note_id)

    await callback.message.edit_text(text=f"🎉 Вы выполнили дедлайн <b>{note.note_title}</b>!",
                                     reply_markup=create_inline_kb(width=1,
                                                                   dct={f"undone_{note_id}_{time_left}": "❌ Не вполнил"}))


@router.callback_query(F.data.startswith("undone_"))
async def undone(callback: CallbackQuery):
    note_id = int(callback.data.split('_')[1])

    time_left = str(callback.data.split('_')[2])

    note = db_manager.get_note(note_id=note_id)

    if note and note.user_id == callback.from_user.id:
        pass
    else:
        if note:
            await callback.answer("❌ Это не ваш дедлайн.")
        else:
            await callback.answer("❌ Такого дедлайна не существует.")
        return

    db_manager.mark_note_as_uncompleted(note_id=note_id)
    schedule_notification(note_id=note_id, deadline_end=note.data_end)

    await callback.message.edit_text(text=f"⏰ Осталось {time_left} до дедлайна <b>{note.title}</b>. Успейте выполнить!",
                                     reply_markup=get_notification_keyboard(note_id=note_id, time_left=time_left))


@router.callback_query(F.data.startswith("complete_"))
async def complete(callback: CallbackQuery):
    note_id = int(callback.data.split('_')[1])

    note = db_manager.get_note(note_id=note_id)

    if note and note.user_id == callback.from_user.id:
        pass
    else:
        if note:
            await callback.answer("❌ Это не ваш дедлайн.")
        else:
            await callback.answer("❌ Такого дедлайна не существует.")
        return

    db_manager.mark_note_as_completed(note_id=note_id)
    cancel_scheduled_notification(note_id=note_id)

    note.is_completed = True

    note_text = get_note_text(note)

    reply_markup = get_note_keyboard(note_id, is_done_kb=note.is_completed)

    await callback.message.edit_text(text=note_text, reply_markup=reply_markup)


@router.callback_query(F.data.startswith("uncomplete_"))
async def uncomplete(callback: CallbackQuery):
    note_id = int(callback.data.split('_')[1])

    note = db_manager.get_note(note_id=note_id)

    if note and note.user_id == callback.from_user.id:
        pass
    else:
        if note:
            await callback.answer("❌ Это не ваш дедлайн.")
        else:
            await callback.answer("❌ Такого дедлайна не существует.")
        return

    db_manager.mark_note_as_uncompleted(note_id=note_id)
    schedule_notification(note_id=note_id, deadline_end=note.data_end)

    note.is_completed = False

    note_text = get_note_text(note)

    reply_markup = get_note_keyboard(note_id, is_done_kb=note.is_completed)

    await callback.message.edit_text(text=note_text, reply_markup=reply_markup)
