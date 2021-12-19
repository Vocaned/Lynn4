import asyncio
import typing
import hikari
import lightbulb


class DynamicButtonNavigator:
    def __init__(
        self,
        callback: typing.Coroutine,
        *,
        buttons: typing.Sequence[lightbulb.utils.ComponentButton] = None,
        timeout: float = 120
    ) -> None:
        self._timeout: float = timeout
        self.index: int = 0
        self.callback = callback

        self.buttons = buttons if buttons is not None else self.create_default_buttons()

        self._context: typing.Optional[lightbulb.Context] = None
        self._msg: typing.Optional[hikari.Message] = None
        self._timeout_task: typing.Optional[asyncio.Task[None]] = None

    async def _send_initial_msg(self, page) -> hikari.Message:
        assert self._context is not None
        buttons = await self.build_buttons()
        resp = await self._context.respond(page, component=buttons)
        return await resp.message()

    async def _edit_msg(self, inter: hikari.ComponentInteraction, page) -> None:
        buttons = await self.build_buttons(disabled=True if self._msg is None else False)
        try:
            await inter.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, page, component=buttons)
        except hikari.NotFoundError:
            await inter.edit_initial_response(page, component=buttons)

    async def build_buttons(self, disabled: bool = False):
        assert self._context is not None
        buttons = self._context.app.rest.build_action_row()
        for button in self.buttons:
            button.build(buttons, disabled)
        return buttons

    async def _process_interaction_create(self, event: hikari.InteractionCreateEvent) -> None:
        if not isinstance(event.interaction, hikari.ComponentInteraction):
            return

        if self._msg is None:
            return

        assert self._context is not None

        if event.interaction.message.id != self._msg.id or event.interaction.user.id != self._context.author.id:
            return

        for button in self.buttons:
            if button.is_pressed(event):
                await button.press(self, event)
                if self._msg is not None:
                    await self._edit_msg(event.interaction, await self.callback(self.index))
                break

    async def _remove_listener(self) -> None:
        assert self._context is not None
        self._context.app.unsubscribe(hikari.InteractionCreateEvent, self._process_interaction_create)

        if self._msg is not None:
            await self._msg.edit(component=await self.build_buttons(True))

    async def _timeout_coro(self) -> None:
        try:
            await asyncio.sleep(self._timeout)
            await self._remove_listener()
        except asyncio.CancelledError:
            pass

    async def next_page(self, nav, _: hikari.Event) -> None:
        nav.index += 1

    async def prev_page(self, nav, _: hikari.Event) -> None:
        nav.index -= 1
        if nav.index < 1:
            nav.index = 0

    async def stop(self, nav, _: hikari.Event) -> None:
        assert nav._msg is not None
        await nav._remove_listener()
        await nav._msg.delete()
        nav._msg = None
        if nav._timeout_task is not None:
            nav._timeout_task.cancel()

    def create_default_buttons(self) -> typing.Sequence[lightbulb.utils.ComponentButton]:
        buttons = [
            lightbulb.utils.ComponentButton(
                "\N{BLACK LEFT-POINTING TRIANGLE}\N{VARIATION SELECTOR-16}",
                True,
                hikari.ButtonStyle.PRIMARY,
                "prev_page",
                self.prev_page,
            ),
            lightbulb.utils.ComponentButton(
                "\N{BLACK SQUARE FOR STOP}\N{VARIATION SELECTOR-16}", True, hikari.ButtonStyle.DANGER, "stop", self.stop
            ),
            lightbulb.utils.ComponentButton(
                "\N{BLACK RIGHT-POINTING TRIANGLE}\N{VARIATION SELECTOR-16}",
                True,
                hikari.ButtonStyle.PRIMARY,
                "next_page",
                self.next_page,
            )
        ]
        return buttons

    async def run(self, context: lightbulb.Context) -> None:
        """
        Run the navigator under the given context.

        Args:
            context (:obj:`~.context.base.Context`): Context
                to run the navigator under.

        Returns:
            ``None``
        """
        self._context = context
        context.app.subscribe(hikari.InteractionCreateEvent, self._process_interaction_create)
        self._msg = await self._send_initial_msg(await self.callback(self.index))

        if self._timeout_task is not None:
            self._timeout_task.cancel()
        self._timeout_task = asyncio.create_task(self._timeout_coro())
