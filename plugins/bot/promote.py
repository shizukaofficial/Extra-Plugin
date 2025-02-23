from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from telegram.error import BadRequest
from config import BOT_TOKEN

async def promoteFunc(update: Update, context: CallbackContext):
    try:
        # Check if the command has arguments or if the user is replying to a message
        if len(context.args) < 1 and not update.message.reply_to_message:
            await update.message.reply_text("Usage: /promote <user_id/username/reply_to_user> <admin_title (optional)>")
            return

        # Extract user from command arguments or replied message
        if update.message.reply_to_message:
            user_id = update.message.reply_to_message.from_user.id  # Use the replied user's ID
        else:
            user = context.args[0]  # Use the provided user ID or username
            try:
                # Try to convert to integer (in case of user ID)
                user_id = int(user)
            except ValueError:
                # If it's not a user ID, assume it's a username and extract the user
                try:
                    user_obj = await context.bot.get_chat_member(update.message.chat_id, user)
                    user_id = user_obj.user.id
                except BadRequest:
                    await update.message.reply_text("Invalid user ID or username.")
                    return

        # Extract admin title if provided
        admin_title = " ".join(context.args[1:]) if len(context.args) > 1 else "Admin"

        # Promote the user with basic permissions
        await context.bot.promote_chat_member(
            chat_id=update.message.chat_id,
            user_id=user_id,
            can_change_info=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=False,  # Basic promote does not allow promoting others
            custom_title=admin_title,  # Set custom admin title
        )

        # Notify the chat about the promotion
        user_mention = f"[{user_obj.user.first_name}](tg://user?id={user_id})"
        await update.message.reply_text(f"Promoted {user_mention} with title: {admin_title}", parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"Failed to promote user: {e}")

async def fullpromoteFunc(update: Update, context: CallbackContext):
    try:
        # Check if the command has arguments or if the user is replying to a message
        if len(context.args) < 1 and not update.message.reply_to_message:
            await update.message.reply_text("Usage: /fullpromote <user_id/username/reply_to_user> <admin_title (optional)>")
            return

        # Extract user from command arguments or replied message
        if update.message.reply_to_message:
            user_id = update.message.reply_to_message.from_user.id  # Use the replied user's ID
        else:
            user = context.args[0]  # Use the provided user ID or username
            try:
                # Try to convert to integer (in case of user ID)
                user_id = int(user)
            except ValueError:
                # If it's not a user ID, assume it's a username and extract the user
                try:
                    user_obj = await context.bot.get_chat_member(update.message.chat_id, user)
                    user_id = user_obj.user.id
                except BadRequest:
                    await update.message.reply_text("Invalid user ID or username.")
                    return

        # Extract admin title if provided
        admin_title = " ".join(context.args[1:]) if len(context.args) > 1 else "Full Admin"

        # Promote the user with full permissions
        await context.bot.promote_chat_member(
            chat_id=update.message.chat_id,
            user_id=user_id,
            can_change_info=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=True,  # Full promote allows promoting others
            custom_title=admin_title,  # Set custom admin title
        )

        # Notify the chat about the promotion
        user_mention = f"[{user_obj.user.first_name}](tg://user?id={user_id})"
        await update.message.reply_text(f"Fully promoted {user_mention} with title: {admin_title}", parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"Failed to fully promote user: {e}")

# Add the command handlers to your application
from telegram.ext import Application
application = Application.builder().token("BOT_TOKEN").build()

# Register the /promote and /fullpromote commands
application.add_handler(CommandHandler("promote", promoteFunc))
application.add_handler(CommandHandler("fullpromote", fullpromoteFunc))

# Start the bot
application.run_polling()