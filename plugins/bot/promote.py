import logging
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Application
from telegram.error import BadRequest
from config import BOT_TOKEN
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def extract_user_info(update: Update, context: CallbackContext):
    """Extract user ID from command arguments or replied message."""
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user.id
    else:
        user = context.args[0]
        try:
            return int(user)  # Try to convert to integer (user ID)
        except ValueError:
            try:
                user_obj = await context.bot.get_chat_member(update.message.chat_id, user)
                return user_obj.user.id
            except BadRequest:
                await update.message.reply_text("Invalid user ID or username.")
                return None

async def promote_user(update: Update, context: CallbackContext, full_permissions=False):
    """Promote a user with specified permissions."""
    try:
        if len(context.args) < 1 and not update.message.reply_to_message:
            await update.message.reply_text(f"Usage: /{'full' if full_permissions else ''}promote <user_id/username/reply_to_user> <admin_title (optional)>")
            return

        user_id = await extract_user_info(update, context)
        if not user_id:
            return

        admin_title = " ".join(context.args[1:]) if len(context.args) > 1 else ("Full Admin" if full_permissions else "Admin")

        permissions = {
            'can_change_info': True,
            'can_delete_messages': True,
            'can_invite_users': True,
            'can_restrict_members': True,
            'can_pin_messages': True,
            'can_promote_members': full_permissions,
        }

        await context.bot.promote_chat_member(
            chat_id=update.message.chat_id,
            user_id=user_id,
            **permissions,
            custom_title=admin_title,
        )

        user_mention = f"[{update.message.reply_to_message.from_user.first_name if update.message.reply_to_message else context.args[0]}](tg://user?id={user_id})"
        await update.message.reply_text(f"{'Fully promoted' if full_permissions else 'Promoted'} {user_mention} with title: {admin_title}", parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Failed to promote user: {e}")
        await update.message.reply_text(f"Failed to promote user: {e}")

async def promoteFunc(update: Update, context: CallbackContext):
    """Promote a user with basic permissions."""
    await promote_user(update, context, full_permissions=False)

async def fullpromoteFunc(update: Update, context: CallbackContext):
    """Promote a user with full permissions."""
    await promote_user(update, context, full_permissions=True)

# Register command handlers
def register_handlers(application: Application):
    application.add_handler(CommandHandler("promote", promoteFunc))
    application.add_handler(CommandHandler("fullpromote", fullpromoteFunc))

# Example usage
if __name__ == "__main__":
    application = Application.builder().token("BOT_TOKEN").build()
    register_handlers(application)
    application.run_polling()