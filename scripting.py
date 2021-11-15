"""
saved in data/scripts/[guildId].json
overwrites existing commands
Disable ping command:
"/ping": ""
Custom alias:
"/pong": "ping()"
Pass arguments to command:
"/helsinki": "weather(helsinki)"
Command chaining (run everything even if one fails):
"/alias": "weather(), echo(weather command needs a location)"
Command chanining (stop if a command fails):
"/alias": "weather() + echo(this will never run)"
Command chaining and user input (pass output to another command):
"/alias 10 100": "rand($1) + rand($2) + echo(rand 0-$1: $$1, rand 0-$2: $$2)"
Get author's name and full input
"/alias this is a message": "echo($author said `$0`)"
Respond to message instead of command:
"msg": "echo(this will run when someone types the message \"msg\" in chat)"
Respond to partial message:
"*msg": "echo(this will run when someone types the word \"msg\" in chat, even if it's a part of a longer message)"
Signs can also be escaped:
"\*msg": "echo(you typed *msg)"
Case-insensitive match + helper commands:
"^xd": "echo(xD)"
"^*xd": "is_channel_id(855110888057995285) + echo(no saying xd in this channel) + purge($message_id)"
Executed in order:
scripting commands -> default commands -> message matches
"""
import os
import re
import json
import hikari
import lynn

class Scripting:
    def __init__(self, bot) -> None:
        self.bot = bot

    async def handler(self, event: hikari.MessageCreateEvent) -> None:
        # Ignore custom command stuff if guild has no custom commands
        scriptpath = os.path.join('data', 'configs', f'{event.message.guild_id}_scripting.json')
        if not os.path.exists(scriptpath):
            await self.bot.process_commands_for_event(event)
            return

        with open(scriptpath, 'r', encoding='utf-8') as f:
            rules = json.load(f)

        await self.handle_scripting_commands(event, rules)
        await self.bot.process_commands_for_event(event)
        await self.handle_scripting_message(event, rules)


    async def handle_scripting_commands(self, event: hikari.MessageCreateEvent, rules: list) -> None:
        prefix = await self.bot._resolve_prefix(event.message)
        if prefix is None:
            return

        new_content = event.message.content[len(prefix):]
        if not new_content or new_content.isspace():
            return

        cmd, args = new_content.split(None, maxsplit=1)

        for rule, script in rules:
            if not rule[0] == '/':
                continue # Only handle commands in this step

            if cmd == rule[1:]:
                self.execute_script(event, script, args)

    async def handle_scripting_message(self, event: hikari.MessageCreateEvent, rules: list) -> None:
        # TODO: handle escape characters
        for rule, script in rules:
            if rule[0] == '*':
                if rule[1:] in event.message.content:
                    self.execute_script(event, script, event.message.content)

            elif rule[0] == '^':
                if rule[1] == '*' and rule[1:].lower() in event.message.content.lower():
                    self.execute_script(event, script, event.message.content)
                elif rule[1:].lower() == event.message.content.lower():
                    self.execute_script(event, script, event.message.content)

            elif rule == event.message.content:
                self.execute_script(event, script, event.message.content)

    async def execute_script(self, event: hikari.MessageCreateEvent, script: str, args: str):
        logic = []
        for op, arg in re.findall(r'(.*?)(\(.*?\))*(?=\s|$)', script):
            pass
