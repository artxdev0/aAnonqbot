
from bot_base import *

####

kb_main_menu = ikb([
    ('❓ Мої запитання', 'myquestions')
])


@client.on_message(filters.command('start'))
@cmd_error_handling
async def cmd_start(_, msg: types.Message):
    is_new = False
    with Session(engine) as session:
        
        u = session.query(database.User).where(database.User.user_id == msg.from_user.id).one_or_none()
        if u is None:
            u = database.User(
                user_id=msg.from_user.id,
                user_link=random_string(config['user_link_min_length'] + max(1, int(session.query(database.User).count() / config['user_link_length_threshold']))),
            )
            session.add(u)
            session.commit()
            is_new = False
            logger.info('{} (@{}, {}) is new user!', msg.from_user.first_name, msg.from_user.username, msg.from_user.id)

        bot_un = (await client.get_me()).username
        
        if len(msg.command) > 1:
            link = msg.command[1]
            
            to_user = session.query(database.User).where(database.User.user_link == link).one_or_none()
            if to_user is None:
                await msg.reply(f'''
❌ На жаль щось пішло не так, скоріш за всього посилання некоректне.

🔗 Ось твоє посилання для анонимних питань: t.me/{bot_un}?start={u.user_link}
'''.strip())
                return
        
            m = await client.ask(chat_id=msg.from_user.id, text='✍️ Напиши повідомлення чи пришли аудіо, відео, фото, голосове повідомлення чи файл.', filters=filters.text | filters.audio | filters.video | filters.photo | filters.voice | filters.document, timeout=3600)
            
            if m is None:
                await msg.reply(f'''
❌ Повідомлення скасовано!

🔗 Ось твоє посилання для анонимних питань: t.me/{bot_un}?start={u.user_link}
'''.strip())
                return
            
            if m.text is not None:
                if m.text.startswith('/'):
                    await msg.reply(f'''
❌ Повідомлення скасовано!

🔗 Ось твоє посилання для анонимних питань: t.me/{bot_un}?start={u.user_link}
'''.strip())
                    return
            
            try:
                if m.photo is not None:
                    await client.send_photo(to_user.user_id, m.photo.file_id, f'👁‍🗨📥 Тобі прийшла анонимна картинка!'.strip() + f'\n\n💬 `{m.caption}`' if m.caption is not None else '', reply_markup=ikb([
    [('Відповісти', f'write:{u.user_link}')]
]))
                elif m.audio is not None:
                    await client.send_audio(to_user.user_id, m.audio.file_id, f'👁‍🗨📥 Тобі прийшло анонимне аудіо!'.strip() + f'\n\n💬 `{m.audio.caption}`' if m.audio.caption is not None else '', duration=m.audio.duration, performer=m.audio.performer, reply_markup=ikb([
    [('Відповісти', f'write:{u.user_link}')]
]))
                elif m.video is not None:
                    await client.send_video(to_user.user_id, m.video.file_id, f'👁‍🗨📥 Тобі прийшло анонимне відео!'.strip() + f'\n\n💬 `{m.video.caption}`' if m.video.caption is not None else '', duration=m.video.duration, reply_markup=ikb([
    [('Відповісти', f'write:{u.user_link}')]
]))
                elif m.voice is not None:
                    await client.send_voice(to_user.user_id, m.voice.file_id, f'👁‍🗨📥 Тобі прийшло анонимне голосове повідомлення!'.strip() + f'\n\n💬 `{m.text}`' if m.text is not None else '', duration=m.voice.duration, reply_markup=ikb([
    [('Відповісти', f'write:{u.user_link}')]
]))
                elif m.document is not None:
                    await client.send_document(to_user.user_id, m.document.file_id, caption=f'👁‍🗨📥 Тобі прийшло анонимний файл!'.strip() + f'\n\n💬 `{m.text}`' if m.text is not None else '', file_name=m.document.file_name, reply_markup=ikb([
    [('Відповісти', f'write:{u.user_link}')]
]))
                else:
                    await client.send_message(to_user.user_id, f'''
👁‍🗨📥 Тобі прийшло анонимне повідомлення!

💬 `{m.text}`
'''.strip(), reply_markup=ikb([
    [('Відповісти', f'write:{u.user_link}')]
]))
            except Exception as e:
                logger.exception('handled exception in /{}: {}', 'start', e)
                await msg.reply(f'''
❌ Повідомлення неможливо відправити!
Мабуть отримувач заблокував бота.

🔗 Ось твоє посилання для анонимних питань: t.me/{bot_un}?start={u.user_link}
'''.strip())
                return

            await m.delete()
            await m.sent_message.delete()        
        
            if m.photo is not None:
                await client.send_photo(msg.from_user.id, m.photo.file_id, f'👁‍🗨📤 Ти надіслав анонимну картинку!'.strip() + f'\n\n💬 `{m.caption}`' if m.caption is not None else '', reply_markup=ikb([
    [('Написати ще', f'write:{to_user.user_link}')]
]))
            elif m.audio is not None:
                await client.send_audio(msg.from_user.id, m.audio.file_id, f'👁‍🗨📤 Ти надіслав анонимне аудіо!'.strip() + f'\n\n💬 `{m.audio.caption}`' if m.audio.caption is not None else '', duration=m.audio.duration, performer=m.audio.performer, reply_markup=ikb([
    [('Написати ще', f'write:{to_user.user_link}')]
]))
            elif m.video is not None:
                await client.send_video(msg.from_user.id, m.video.file_id, f'👁‍🗨📤 Ти надіслав анонимне відео!'.strip() + f'\n\n💬 `{m.video.caption}`' if m.video.caption is not None else '', duration=m.video.duration, reply_markup=ikb([
    [('Написати ще', f'write:{to_user.user_link}')]
]))
            elif m.voice is not None:
                await client.send_voice(msg.from_user.id, m.voice.file_id, f'👁‍🗨📤 Ти надіслав анонимне голосове повідомлення!'.strip() + f'\n\n💬 `{m.text}`' if m.text is not None else '', duration=m.voice.duration, reply_markup=ikb([
    [('Написати ще', f'write:{to_user.user_link}')]
]))
            elif m.document is not None:
                await client.send_document(msg.from_user.id, m.document.file_id, caption=f'👁‍🗨📤 Ти надіслав анонимний файл!'.strip() + f'\n\n💬 `{m.text}`' if m.text is not None else '', file_name=m.document.file_name, reply_markup=ikb([
    [('Написати ще', f'write:{to_user.user_link}')]
]))
            else:
                await client.send_message(msg.from_user.id, f'''
👁‍🗨📤 Ти надіслав повідомлення!

💬 `{m.text}`
'''.strip(), reply_markup=ikb([
    [('Написати ще', f'write:{to_user.user_link}')]
]))
            if not is_new:
                return

        await msg.reply(f'''
✋ Привіт! Я листоноша анонимних питань чи повідомлень!

🔗 Ось твоє посилання для анонимних повідомлень: t.me/{bot_un}?start={u.user_link}

👁‍🗨 Додай посилання у твій ТГК чи статус аккаунту та отримуй анонимні повідомлення!
'''.strip()
        )

####


@client.on_callback_query(cbfilter_param('write:'))
@q_error_handling
async def q_write(_, q: types.CallbackQuery):
    with Session(engine) as session:
        
        u = session.query(database.User).where(database.User.user_id == q.from_user.id).one_or_none()
        if u is None:
            u = database.User(
                user_id=q.from_user.id,
                user_link=random_string(config['user_link_min_length'] + max(1, int(session.query(database.User).count() / config['user_link_length_threshold']))),
            )
            session.add(u)
            session.commit()

        bot_un = (await client.get_me()).username
        link = q.data[6:]
        
        to_user = session.query(database.User).where(database.User.user_link == link).one_or_none()
        if to_user is None:
            await q.message.reply(f'''
❌ На жаль щось пішло не так, скоріш за всього посилання некоректне.

🔗 Ось твоє посилання для анонимних питань: t.me/{bot_un}?start={u.user_link}
'''.strip())
            return
        
        m = await client.ask(chat_id=q.from_user.id, text='✍️ Напиши повідомлення чи пришли аудіо, відео, фото, голосове повідомлення чи файл.', filters=filters.text | filters.audio | filters.video | filters.voice | filters.photo | filters.document, timeout=3600)
        if m is None:
            await q.message.reply(f'''
❌ Повідомлення скасовано!

🔗 Ось твоє посилання для анонимних питань: t.me/{bot_un}?start={u.user_link}
'''.strip())
            return
                
        try:
            if m.photo is not None:
                await client.send_photo(to_user.user_id, m.photo.file_id, f'👁‍🗨📥 Тобі прийшла анонимна картинка!'.strip() + f'\n\n💬 `{m.caption}`' if m.caption is not None else '', reply_markup=ikb([
    [('Відповісти', f'write:{u.user_link}')]
]))
            elif m.audio is not None:
                await client.send_audio(to_user.user_id, m.audio.file_id, f'👁‍🗨📥 Тобі прийшло анонимне аудіо!'.strip() + f'\n\n💬 `{m.audio.caption}`' if m.audio.caption is not None else '', duration=m.audio.duration, performer=m.audio.performer, reply_markup=ikb([
    [('Відповісти', f'write:{u.user_link}')]
]))
            elif m.video is not None:
                await client.send_video(to_user.user_id, m.video.file_id, f'👁‍🗨📥 Тобі прийшло анонимне відео!'.strip() + f'\n\n💬 `{m.video.caption}`' if m.video.caption is not None else '', duration=m.video.duration, reply_markup=ikb([
    [('Відповісти', f'write:{u.user_link}')]
]))
            elif m.voice is not None:
                await client.send_voice(to_user.user_id, m.voice.file_id, f'👁‍🗨📥 Тобі прийшло анонимне голосове повідомлення!'.strip() + f'\n\n💬 `{m.text}`' if m.text is not None else '', duration=m.voice.duration, reply_markup=ikb([
    [('Відповісти', f'write:{u.user_link}')]
]))
            elif m.document is not None:
                await client.send_document(to_user.user_id, m.document.file_id, caption=f'👁‍🗨📥 Тобі прийшов анонимний файл!'.strip() + f'\n\n💬 `{m.text}`' if m.text is not None else '', file_name=m.document.file_name, reply_markup=ikb([
    [('Відповісти', f'write:{u.user_link}')]
]))
            else:
                await client.send_message(to_user.user_id, f'''
👁‍🗨📥 Тобі прийшло анонимне повідомлення!

💬 `{m.text}`
'''.strip(), reply_markup=ikb([
    [('Відповісти', f'write:{u.user_link}')]
]))
        except Exception as e:
            logger.exception('handled exception in /{}: {}', 'start', e)
            await q.message.reply(f'''
❌ Повідомлення неможливо відправити!
Мабуть отримувач заблокував бота.

🔗 Ось твоє посилання для анонимних питань: t.me/{bot_un}?start={u.user_link}
'''.strip())
            return

        await m.delete()
        await m.sent_message.delete()        
        
        
        if m.photo is not None:
            await client.send_photo(q.from_user.id, m.photo.file_id, f'👁‍🗨📤 Ти надіслав анонимну картинка!'.strip() + f'\n\n💬 `{m.caption}`' if m.caption is not None else '', reply_markup=ikb([
    [('Написати ще', f'write:{to_user.user_link}')]
]))
        elif m.audio is not None:
            await client.send_audio(q.from_user.id, m.audio.file_id, f'👁‍🗨📤 Ти надіслав анонимне аудіо!'.strip() + f'\n\n💬 `{m.audio.caption}`' if m.audio.caption is not None else '', duration=m.audio.duration, performer=m.audio.performer, reply_markup=ikb([
    [('Написати ще', f'write:{to_user.user_link}')]
]))
        elif m.video is not None:
            await client.send_video(q.from_user.id, m.video.file_id, f'👁‍🗨📤 Ти надіслав анонимне відео!'.strip() + f'\n\n💬 `{m.video.caption}`' if m.video.caption is not None else '', duration=m.video.duration, reply_markup=ikb([
    [('Написати ще', f'write:{to_user.user_link}')]
]))
        elif m.voice is not None:
            await client.send_voice(q.from_user.id, m.voice.file_id, f'👁‍🗨📤 Ти надіслав анонимне голосове повідомлення!'.strip() + f'\n\n💬 `{m.text}`' if m.text is not None else '', duration=m.voice.duration, reply_markup=ikb([
    [('Написати ще', f'write:{to_user.user_link}')]
]))
        elif m.document is not None:
            await client.send_document(q.from_user.id, m.document.file_id, caption=f'👁‍🗨📤 Ти надіслав панонимний файл!'.strip() + f'\n\n💬 `{m.text}`' if m.text is not None else '', file_name=m.document.file_name, reply_markup=ikb([
    [('Написати ще', f'write:{to_user.user_link}')]
]))
        else:
            await client.send_message(q.from_user.id, f'''
👁‍🗨📤 Ти надіслав повідомлення!

💬 `{m.text}`
'''.strip(), reply_markup=ikb([
    [('Написати ще', f'write:{to_user.user_link}')]
]))
            return

####

if __name__ == '__main__':
    client.run()
