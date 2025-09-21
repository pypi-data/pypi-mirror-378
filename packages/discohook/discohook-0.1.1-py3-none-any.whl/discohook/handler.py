import asyncio

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .command import ApplicationCommand, ApplicationCommandOptionType
from .enums import (
    ApplicationCommandType,
    ComponentType,
    InteractionCallbackType,
    InteractionType,
)
from .errors import CheckFailure, UnknownInteractionType, InteractionException
from .interaction import Interaction
from .resolver import (
    build_context_menu_param,
    build_modal_params,
    build_select_menu_values,
    build_slash_command_params,
)


def _build_key(interaction: Interaction) -> str:
    specific_source_guild = interaction.data.get("guild_id")
    if specific_source_guild:
        return f"{interaction.data['name']}:{specific_source_guild}:{interaction.data['type']}"
    return f"{interaction.data['name']}:{interaction.data['type']}"


# noinspection PyProtectedMember
async def _handler(request: Request):
    """
    Handles all interactions from discord

    Note: This is not a public API and should not be used outside the library
    """
    signature = bytes.fromhex(request.headers.get("X-Signature-Ed25519", ""))
    timestamp = request.headers.get("X-Signature-Timestamp", "")
    message = timestamp.encode() + await request.body()
    public_key = bytes.fromhex(request.app.public_key)
    try:
        VerifyKey(public_key).verify(message, signature)
    except BadSignatureError:
        return Response(content="BadSignature", status_code=401)
    data = await request.json()
    interaction = Interaction(request.app, data)
    try:
        if interaction.type == InteractionType.ping:
            return JSONResponse({"type": InteractionCallbackType.pong}, status_code=200)

        elif interaction.type == InteractionType.app_command:
            cmd: ApplicationCommand = request.app.commands.get(_build_key(interaction))
            if not cmd:
                raise NotImplementedError(
                    f"command `{interaction.data['name']}` ({interaction.data['id']}) not found"
                )
            try:
                if cmd.checks:
                    results = await asyncio.gather(
                        *[check(interaction) for check in cmd.checks]
                    )
                    for result in results:
                        if not isinstance(result, bool):
                            raise CheckFailure(
                                f"check returned {type(result)}, expected bool",
                                interaction
                            )
                    if not all(results):
                        raise CheckFailure(f"command checks failed", interaction)

                if not (interaction.data["type"] == ApplicationCommandType.slash):
                    await cmd(interaction, build_context_menu_param(interaction))

                elif interaction.data.get("options") and (
                    interaction.data["options"][0]["type"]
                    == ApplicationCommandOptionType.subcommand
                ):
                    subcommand = cmd.subcommands[interaction.data["options"][0]["name"]]
                    args, kwargs = build_slash_command_params(
                        subcommand.callback, interaction
                    )
                    await subcommand(interaction, *args, **kwargs)
                else:
                    args, kwargs = build_slash_command_params(cmd.callback, interaction)
                    await cmd(interaction, *args, **kwargs)
            except Exception as e:
                if not cmd._error_handler:
                    raise e
                await cmd._error_handler(InteractionException(str(e), interaction))

        elif interaction.type == InteractionType.autocomplete:
            cmd: ApplicationCommand = request.app.commands.get(_build_key(interaction))
            if not cmd:
                raise Exception(
                    f"command `{interaction.data['name']}` ({interaction.data['id']}) not found"
                )
            if (
                interaction.data["options"][0]["type"]
                == ApplicationCommandOptionType.subcommand
            ):
                subcommand = cmd.subcommands[interaction.data["options"][0]["name"]]
                args, kwargs = build_slash_command_params(
                    subcommand.autocompletion_handler, interaction
                )
                await subcommand.autocompletion_handler(interaction, *args, **kwargs)
            elif not cmd.autocompletion_handler:
                raise Exception(
                    f"command `{interaction.data['name']}` ({interaction.data['id']}) has no autocompletion handler"
                )
            else:
                args, kwargs = build_slash_command_params(
                    cmd.autocompletion_handler, interaction
                )
                await cmd.autocompletion_handler(interaction, *args, **kwargs)

        elif interaction.type in (
            InteractionType.component,
            InteractionType.modal_submit,
        ):
            custom_id = interaction.data["custom_id"]
            if request.app._custom_id_parser:
                custom_id = await request.app._custom_id_parser(interaction, custom_id)
            component = request.app.active_components.get(custom_id)
            if not component:
                raise NotImplementedError(f"component `{custom_id}` not found")
            try:
                if component.checks:
                    results = await asyncio.gather(
                        *[check(interaction) for check in component.checks]
                    )
                    for result in results:
                        if not isinstance(result, bool):
                            raise CheckFailure(
                                f"check returned {type(result)}, expected bool",
                                interaction
                            )
                    if not all(results):
                        raise CheckFailure("component checks failed", interaction)

                if interaction.type == InteractionType.component:
                    if interaction.data["component_type"] == ComponentType.button:
                        await component(interaction)
                    else:
                        await component(
                            interaction, build_select_menu_values(interaction)
                        )
                elif interaction.type == InteractionType.modal_submit:
                    args, kwargs = build_modal_params(component.callback, interaction)
                    await component(interaction, *args, **kwargs)
            except Exception as e:
                if not component._error_handler:
                    raise e
                await component._error_handler(InteractionException(str(e), interaction))
        else:
            raise UnknownInteractionType(f"unknown interaction type {interaction.type}", interaction)
    except Exception as e:
        if request.app._interaction_error_handler:
            await request.app._interaction_error_handler(InteractionException(str(e), interaction))
            return Response(status_code=500)
        else:
            raise e from None
    else:
        return Response(status_code=200)
