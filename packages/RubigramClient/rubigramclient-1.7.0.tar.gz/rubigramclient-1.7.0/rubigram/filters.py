from rubigram.types import Update, InlineMessage
from typing import Union
import re



class Filter:
    def __init__(self, func):
        self.func = func
    
    async def __call__(self, update: Union[Update, InlineMessage]):
        return await self.func(update)
    
    def __and__(self, other: "Filter"):
        async def filter(update):
            return await self(update) and await other(update)
        return Filter(filter)
    
    def __or__(self, other: "Filter"):
        async def filter(update):
            return await self(update) or await other(update)
        return Filter(filter)



async def TEXT(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.text or message.updated_message.text else False
    return False

async def FILE(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.file else False
    return False

async def LIVE(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.live_location else False
    return False

async def POLL(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.poll else False
    return False

async def CONTACT(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.contact_message else False
    return False

async def STICKER(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.sticker else False
    return False

async def LOCATION(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.location else False
    return False

async def FORWARD(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.forwarded_from else False
    return False

async def EDITED(message: Update):
    if isinstance(message, Update):
        return True if message.updated_message else False
    return False

async def PRIVATE(message: Union[Update, InlineMessage]):
    return True if message.chat_id.startswith("b0") else False
    
async def GROUP(message: Union[Update, InlineMessage]):
    return True if message.chat_id.startswith("g0") else False

async def CHANNEL(message: Union[Update, InlineMessage]):
    return True if message.chat_id.startswith("c0") else False

async def FORWARD_BOT(message: Update):
    if isinstance(message, Update) and message.new_message:
        return True if message.new_message.forwarded_from and message.new_message.forwarded_from.type_from == "Bot" else False

async def FORWARD_USER(message: Update):
    if isinstance(message, Update) and message.new_message:
        return True if message.new_message.forwarded_from and message.new_message.forwarded_from.type_from == "User" else False
    
async def FORWARD_CHANNEL(message: Update):
    if isinstance(message, Update) and message.new_message:
        return True if message.new_message.forwarded_from and message.new_message.forwarded_from.type_from == "Channel" else False


text = Filter(TEXT)
file = Filter(FILE)
live = Filter(LIVE)
poll = Filter(POLL)
contact = Filter(CONTACT)
sticker = Filter(STICKER)
location = Filter(LOCATION)
forward = Filter(FORWARD)
edited = Filter(EDITED)
private = Filter(PRIVATE)
group = Filter(GROUP)
channel = Filter(CHANNEL)
forward_bot = Filter(FORWARD_BOT)
forward_user = Filter(FORWARD_USER)
forward_channel = Filter(FORWARD_CHANNEL)


class state(Filter):
    def __init__(self, state: Union[str, list[str]]):
        self.states = state if isinstance(state, list) else [state]
        super().__init__(self.filter)
        
    async def filter(self, update: Union[Update, InlineMessage]):
        user_state = await update.client.state.get_state(update.chat_id)
        return user_state in self.states
            

class command(Filter):
    def __init__(self, command: Union[str, list[str]], prefix: Union[str, list[str]] = "/", case_sensitive: bool = False):
        self.commands = [c if case_sensitive else c.lower() for c in (command if isinstance(command, list) else [command])]
        self.prefixs = prefix if isinstance(prefix, list) else [prefix]
        self.cmds = [p + c for p in self.prefixs for c in self.commands]
        self.case_sensitive = case_sensitive
        super().__init__(self.filter)

    async def filter(self, update: Update):
        if isinstance(update, Update):
            if update.new_message:
                text = update.new_message.text
            elif update.updated_message:
                text = update.updated_message.text
            else: return False
            text = text if self.case_sensitive else text.lower()
            return any(text.startswith(cmd) for cmd in self.cmds)
        return False
    

class button(Filter):
    def __init__(self, button_id: Union[str, list[str]], prefix: Union[str, list[str]] = "", case_sensitive: bool = False):
        self.button_ids = [btn_id if case_sensitive else btn_id.lower() for btn_id in (button_id if isinstance(button_id, list) else [button_id])]
        self.prefixs = prefix if isinstance(prefix, list) else [prefix]
        self.btn_ids = [p + b for p in self.prefixs for b in self.button_ids]
        self.case_sensitive = case_sensitive
        super().__init__(self.filter)

    async def filter(self, update: InlineMessage):
        if isinstance(update, InlineMessage):
            text = update.aux_data.button_id or ""
            text = text if self.case_sensitive else text.lower()
            return any(text.startswith(btn) for btn in self.btn_ids)
        return False

class regex(Filter):
    def __init__(self, pattern: str):
        self.pattern = pattern
        super().__init__(self.filter)

    async def filter(self, update: Union[Update, InlineMessage]):
        text = ""
        if isinstance(update, Update):
            if update.type == "NewMessage":
                text = getattr(update.new_message, "text", "")
            elif update.type == "UpdatedMessage":
                text = getattr(update.updated_message, "text", "")
        elif isinstance(update, InlineMessage):
            text = getattr(update, "text", "")

        return bool(re.search(self.pattern, text)) if text else False


class chat(Filter):
    def __init__(self, chat_id: Union[str, list[str]]):
        self.chat_id = chat_id
        super().__init__(self.filter)

    async def filter(self, update: Union[Update, InlineMessage]):
        chat_ids = self.chat_id if isinstance(self.chat_id, list) else [self.chat_id]
        return update.chat_id in chat_ids