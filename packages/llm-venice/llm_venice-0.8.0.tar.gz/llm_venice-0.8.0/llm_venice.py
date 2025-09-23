import base64
import datetime
import json
import os
import pathlib
from typing import Literal, Optional, Union

import click
import httpx
import llm
from llm.default_plugins.openai_models import Chat
from llm.utils import logging_client
from pydantic import ConfigDict, field_validator, Field


class VeniceChatOptions(Chat.Options):
    extra_body: Optional[Union[dict, str]] = Field(
        description=(
            "Additional JSON properties to include in the request body. "
            "When provided via CLI, must be a valid JSON string."
        ),
        default=None,
    )

    @field_validator("extra_body")
    def validate_extra_body(cls, extra_body):
        if extra_body is None:
            return None

        if isinstance(extra_body, str):
            try:
                return json.loads(extra_body)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON in extra_body string")

        if not isinstance(extra_body, dict):
            raise ValueError("extra_body must be a dictionary")

        return extra_body


class VeniceChat(Chat):
    needs_key = "venice"
    key_env_var = "LLM_VENICE_KEY"
    supports_web_search = False

    def __str__(self):
        return f"Venice Chat: {self.model_id}"

    class Options(VeniceChatOptions):
        pass

    def build_kwargs(self, prompt, stream):
        kwargs = super().build_kwargs(prompt, stream)

        if (
            "response_format" in kwargs
            and kwargs["response_format"].get("type") == "json_schema"
        ):
            kwargs["response_format"]["json_schema"]["strict"] = True
            kwargs["response_format"]["json_schema"]["schema"][
                "additionalProperties"
            ] = False

        return kwargs


class VeniceImageOptions(llm.Options):
    model_config = ConfigDict(populate_by_name=True)
    negative_prompt: Optional[str] = Field(
        description="Negative prompt to guide image generation away from certain features",
        default=None,
    )
    style_preset: Optional[str] = Field(
        description="Style preset to use for generation", default=None
    )
    height: Optional[int] = Field(
        description="Height of generated image", default=1024, ge=64, le=1280
    )
    width: Optional[int] = Field(
        description="Width of generated image", default=1024, ge=64, le=1280
    )
    steps: Optional[int] = Field(
        description="Number of inference steps", default=None, ge=7, le=50
    )
    cfg_scale: Optional[float] = Field(
        description="CFG scale for generation", default=None, gt=0, le=20.0
    )
    seed: Optional[int] = Field(
        description="Random seed for reproducible generation",
        default=None,
        ge=-999999999,
        le=999999999,
    )
    lora_strength: Optional[int] = Field(
        description="LoRA adapter strength percentage", default=None, ge=0, le=100
    )
    safe_mode: Optional[bool] = Field(
        description="Enable safety filters", default=False
    )
    hide_watermark: Optional[bool] = Field(
        description="Hide watermark in generated image", default=True
    )
    return_binary: Optional[bool] = Field(
        description="Return raw binary instead of base64", default=False
    )
    image_format: Optional[Literal["png", "webp"]] = Field(
        description="The image format to return",
        default="png",
        alias="format",
    )
    embed_exif_metadata: Optional[bool] = Field(
        description="Embed prompt generation information in the image's EXIF metadata",
        default=False,
    )
    output_dir: Optional[Union[pathlib.Path, str]] = Field(
        description="Directory to save generated images",
        default=None,
    )
    output_filename: Optional[str] = Field(
        description="Custom filename for saved image", default=None
    )
    overwrite_files: Optional[bool] = Field(
        description="Option to overwrite existing output files", default=False
    )


class VeniceImage(llm.Model):
    can_stream = False
    needs_key = "venice"
    key_env_var = "LLM_VENICE_KEY"

    def __init__(self, model_id, model_name=None):
        self.model_id = f"venice/{model_id}"
        self.model_name = model_id

    def __str__(self):
        return f"Venice Image: {self.model_id}"

    class Options(VeniceImageOptions):
        pass

    def execute(self, prompt, stream, response, conversation=None):
        key = self.get_key()

        options_dict = prompt.options.model_dump(by_alias=True)
        output_dir = options_dict.pop("output_dir", None)
        output_filename = options_dict.pop("output_filename", None)
        overwrite_files = options_dict.pop("overwrite_files", False)
        return_binary = options_dict.get("return_binary", False)
        image_format = options_dict.get("format")

        payload = {
            "model": self.model_name,
            "prompt": prompt.prompt,
            **{k: v for k, v in options_dict.items() if v is not None},
        }

        url = "https://api.venice.ai/api/v1/image/generate"
        headers = {
            "Authorization": f"Bearer {key}",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
        }

        # Logging client option like LLM_OPENAI_SHOW_RESPONSES
        if os.environ.get("LLM_VENICE_SHOW_RESPONSES"):
            client = logging_client()
            r = client.post(url, headers=headers, json=payload, timeout=120)
        else:
            r = httpx.post(url, headers=headers, json=payload, timeout=120)

        try:
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ValueError(f"API request failed: {e.response.text}")

        if r.headers.get("x-venice-is-content-violation") == "true":
            yield "Response marked as content violation; no image was returned."
            return

        if return_binary:
            image_bytes = r.content
        else:
            data = r.json()
            # Store generation parameters including seed in response_json
            response.response_json = {
                "request": data["request"],
                "timing": data["timing"],
            }
            image_data = data["images"][0]
            try:
                image_bytes = base64.b64decode(image_data)
            except Exception as e:
                raise ValueError(f"Failed to decode base64 image data: {e}")

        if output_dir:
            output_dir = pathlib.Path(output_dir)
            if (
                not output_dir.exists()
                or not output_dir.is_dir()
                or not os.access(output_dir, os.W_OK)
            ):
                raise ValueError(f"output_dir {output_dir} is not a writable directory")
        else:
            output_dir = llm.user_dir() / "images"
            output_dir.mkdir(exist_ok=True)

        if not output_filename:
            datestring = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            output_filename = f"{datestring}_venice_{self.model_name}.{image_format}"

        output_filepath = output_dir / output_filename

        # Handle existing files
        if output_filepath.exists() and not overwrite_files:
            stem = output_filepath.stem
            suffix = output_filepath.suffix
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            new_filename = f"{stem}_{timestamp}{suffix}"
            output_filepath = output_dir / new_filename

        try:
            output_filepath.write_bytes(image_bytes)
            yield f"Image saved to {output_filepath}"
        except Exception as e:
            raise ValueError(f"Failed to write image file: {e}")


def image_upscale(
    image_path,
    scale,
    enhance=False,
    enhance_creativity=None,
    enhance_prompt=None,
    replication=None,
    output_path=None,
    overwrite=False,
):
    """
    Upscale an image using Venice AI.

    Example usage:
        llm venice upscale image.jpg --scale 4
    """
    key = llm.get_key("", "venice", "LLM_VENICE_KEY")
    if not key:
        raise click.ClickException("No key found for Venice")

    with open(image_path, "rb") as img_file:
        image_data = img_file.read()

    url = "https://api.venice.ai/api/v1/image/upscale"
    headers = {"Authorization": f"Bearer {key}", "Accept-Encoding": "gzip"}

    # Create multipart form data
    files = {
        "image": (pathlib.Path(image_path).name, image_data),
    }

    data = {
        "scale": scale,
        "enhance": enhance,
        "enhanceCreativity": enhance_creativity,
        "enhancePrompt": enhance_prompt,
        "replication": replication,
    }

    # Remove None values from data in order to use API defaults
    data = {k: v for k, v in data.items() if v is not None}

    r = httpx.post(url, headers=headers, files=files, data=data, timeout=120)

    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed: {e.response.text}")

    image_bytes = r.content

    # Handle output path logic
    input_path = pathlib.Path(image_path)
    # The upscaled image is always PNG
    default_filename = f"{input_path.stem}_upscaled.png"

    if output_path is None:
        # No output path specified, save next to input
        output_path = input_path.parent / default_filename
    else:
        output_path = pathlib.Path(output_path)
        if output_path.is_dir():
            # If output_path is a directory, save there with default filename
            output_path = output_path / default_filename

    # Handle existing files by adding timestamp
    if output_path.exists() and not overwrite:
        stem = output_path.stem
        suffix = output_path.suffix
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{stem}_{timestamp}{suffix}"
        output_path = output_path.parent / new_filename

    try:
        output_path.write_bytes(image_bytes)
        click.echo(f"Upscaled image saved to {output_path}")
    except Exception as e:
        raise ValueError(f"Failed to write image file: {e}")


def refresh_models():
    "Refresh the list of models from the Venice API"
    key = llm.get_key("", "venice", "LLM_VENICE_KEY")
    if not key:
        raise click.ClickException("No key found for Venice")
    headers = {"Authorization": f"Bearer {key}"}

    models = httpx.get(
        "https://api.venice.ai/api/v1/models",
        headers=headers,
        params={"type": "all"},
    )
    models.raise_for_status()
    models = models.json()["data"]

    if not models:
        raise click.ClickException("No models found")
    path = llm.user_dir() / "venice_models.json"
    path.write_text(json.dumps(models, indent=4))
    click.echo(f"{len(models)} models saved to {path}", err=True)

    return models


@llm.hookimpl
def register_commands(cli):
    @cli.group(name="venice")
    def venice():
        "llm-venice plugin commands"

    @venice.command(name="refresh")
    def refresh():
        refresh_models()

    @click.group(name="api-keys", invoke_without_command=True)
    @click.pass_context
    def api_keys(ctx):
        """Manage API keys - list, create, delete, rate-limits"""
        # Retrieve the API key once and store it in context
        key = llm.get_key("", "venice", "LLM_VENICE_KEY")
        if not key:
            raise click.ClickException("No key found for Venice")

        ctx.obj = {"headers": {"Authorization": f"Bearer {key}"}}

        # Default to listing API keys if no subcommand is provided
        if not ctx.invoked_subcommand:
            ctx.invoke(list_keys)

    @api_keys.command(name="list")
    @click.pass_context
    def list_keys(ctx):
        """List all API keys."""
        response = httpx.get(
            "https://api.venice.ai/api/v1/api_keys", headers=ctx.obj["headers"]
        )
        response.raise_for_status()
        click.echo(json.dumps(response.json(), indent=2))

    @api_keys.command(name="rate-limits")
    @click.pass_context
    def rate_limits(ctx):
        "Show current rate limits for your API key"
        response = httpx.get(
            "https://api.venice.ai/api/v1/api_keys/rate_limits",
            headers=ctx.obj["headers"],
        )
        response.raise_for_status()
        click.echo(json.dumps(response.json(), indent=2))

    @api_keys.command(name="rate-limits-log")
    @click.pass_context
    def rate_limits_log(ctx):
        "Show the last 50 rate limit logs for the account"
        response = httpx.get(
            "https://api.venice.ai/api/v1/api_keys/rate_limits/log",
            headers=ctx.obj["headers"],
        )
        response.raise_for_status()
        click.echo(json.dumps(response.json(), indent=2))

    @api_keys.command(name="create")
    @click.option(
        "--type",
        "key_type",
        type=click.Choice(["ADMIN", "INFERENCE"]),
        required=True,
        help="Type of API key",
    )
    @click.option("--description", default="", help="Description for the new API key")
    @click.option(
        "--expiration-date",
        type=click.DateTime(
            formats=[
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M",
                "%Y-%m-%dT%H:%M:%S",
            ]
        ),
        default=None,
        help="The API Key expiration date",
    )
    @click.option(
        "--limits-vcu",
        type=click.FloatRange(min=0.0),
        default=None,
        help="VCU consumption limit per epoch",
    )
    @click.option(
        "--limits-usd",
        type=click.FloatRange(min=0.0),
        default=None,
        help="USD consumption limit per epoch",
    )
    @click.pass_context
    def create_key(ctx, description, key_type, expiration_date, limits_vcu, limits_usd):
        """Create a new API key."""
        payload = {
            "description": description,
            "apiKeyType": key_type,
            "expiresAt": expiration_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            if expiration_date
            else "",
            "consumptionLimit": {
                "vcu": limits_vcu,
                "usd": limits_usd,
            },
        }
        response = httpx.post(
            "https://api.venice.ai/api/v1/api_keys",
            headers=ctx.obj["headers"],
            json=payload,
        )
        response.raise_for_status()
        click.echo(json.dumps(response.json(), indent=2))

    @api_keys.command(name="delete")
    @click.argument("api_key_id")
    @click.pass_context
    def delete_key(ctx, api_key_id):
        """Delete an API key by ID."""
        params = {"id": api_key_id}
        response = httpx.delete(
            "https://api.venice.ai/api/v1/api_keys",
            headers=ctx.obj["headers"],
            params=params,
        )
        response.raise_for_status()
        click.echo(json.dumps(response.json(), indent=2))

    # Register api-keys command group under "venice"
    venice.add_command(api_keys)

    @venice.command(name="characters")
    @click.option(
        "--web-enabled",
        type=click.Choice(["true", "false"]),
        help="Filter by web-enabled status",
    )
    @click.option(
        "--adult", type=click.Choice(["true", "false"]), help="Filter by adult category"
    )
    def characters(web_enabled, adult):
        """List public characters."""
        key = llm.get_key("", "venice", "LLM_VENICE_KEY")
        if not key:
            raise click.ClickException("No key found for Venice")
        headers = {"Authorization": f"Bearer {key}"}
        params = {}
        params = {
            k: v
            for k, v in {"isWebEnabled": web_enabled, "isAdult": adult}.items()
            if v
        }
        response = httpx.get(
            "https://api.venice.ai/api/v1/characters",
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        characters = response.json()
        path = llm.user_dir() / "venice_characters.json"
        path.write_text(json.dumps(characters, indent=4))
        characters_count = len(characters.get("data", []))
        click.echo(f"{characters_count} models saved to {path}", err=True)

    # Remove and store the original prompt and chat commands
    # in order to add them back with custom cli options
    original_prompt = cli.commands.pop("prompt")
    original_chat = cli.commands.pop("chat")

    def process_venice_options(kwargs):
        """Helper to process venice-specific options"""
        no_venice_system_prompt = kwargs.pop("no_venice_system_prompt", False)
        web_search = kwargs.pop("web_search", False)
        character = kwargs.pop("character", None)
        strip_thinking_response = kwargs.pop("strip_thinking_response", False)
        disable_thinking = kwargs.pop("disable_thinking", False)
        options = list(kwargs.get("options", []))
        model_id = kwargs.get("model_id")

        if model_id and model_id.startswith("venice/"):
            model = llm.get_model(model_id)
            venice_params = {}

            if no_venice_system_prompt:
                venice_params["include_venice_system_prompt"] = False

            if web_search:
                if not getattr(model, "supports_web_search", False):
                    raise click.ClickException(
                        f"Model {model_id} does not support web search"
                    )
                venice_params["enable_web_search"] = web_search

            if character:
                venice_params["character_slug"] = character

            if strip_thinking_response:
                venice_params["strip_thinking_response"] = True

            if disable_thinking:
                venice_params["disable_thinking"] = True

            if venice_params:
                # If a Venice option is used, any `-o extra_body value` is overridden here.
                # TODO: Would prefer to remove the extra_body CLI option, but
                # the implementation is required for venice_parameters.
                options.append(("extra_body", {"venice_parameters": venice_params}))
                kwargs["options"] = options

        return kwargs

    # Create new prompt command
    @cli.command(name="prompt")
    @click.option(
        "--no-venice-system-prompt",
        is_flag=True,
        help="Disable Venice AI's default system prompt",
    )
    @click.option(
        "--web-search",
        type=click.Choice(["auto", "on", "off"]),
        help="Enable web search",
    )
    @click.option(
        "--character",
        help="Use a Venice AI public character (e.g. 'alan-watts')",
    )
    @click.option(
        "--strip-thinking-response",
        is_flag=True,
        help="Strip <think></think> blocks from the response (for reasoning models)",
    )
    @click.option(
        "--disable-thinking",
        is_flag=True,
        help="Disable thinking and strip <think></think> blocks (for reasoning models)",
    )
    @click.pass_context
    def new_prompt(ctx, no_venice_system_prompt, web_search, character, strip_thinking_response, disable_thinking, **kwargs):
        """Execute a prompt"""
        kwargs = process_venice_options(
            {
                **kwargs,
                "no_venice_system_prompt": no_venice_system_prompt,
                "web_search": web_search,
                "character": character,
                "strip_thinking_response": strip_thinking_response,
                "disable_thinking": disable_thinking,
            }
        )
        return ctx.invoke(original_prompt, **kwargs)

    # Create new chat command
    @cli.command(name="chat")
    @click.option(
        "--no-venice-system-prompt",
        is_flag=True,
        help="Disable Venice AI's default system prompt",
    )
    @click.option(
        "--web-search",
        type=click.Choice(["auto", "on", "off"]),
        help="Enable web search",
    )
    @click.option(
        "--character",
        help="Use a Venice AI character (e.g. 'alan-watts')",
    )
    @click.option(
        "--strip-thinking-response",
        is_flag=True,
        help="Strip <think></think> blocks from the response (for reasoning models)",
    )
    @click.option(
        "--disable-thinking",
        is_flag=True,
        help="Disable thinking and strip <think></think> blocks (for reasoning models)",
    )
    @click.pass_context
    def new_chat(ctx, no_venice_system_prompt, web_search, character, strip_thinking_response, disable_thinking, **kwargs):
        """Hold an ongoing chat with a model"""
        kwargs = process_venice_options(
            {
                **kwargs,
                "no_venice_system_prompt": no_venice_system_prompt,
                "web_search": web_search,
                "character": character,
                "strip_thinking_response": strip_thinking_response,
                "disable_thinking": disable_thinking,
            }
        )
        return ctx.invoke(original_chat, **kwargs)

    # Copy over all params from original commands
    for param in original_prompt.params:
        if param.name not in (
            "no_venice_system_prompt",
            "web_search",
            "character",
            "strip_thinking_response",
            "disable_thinking",
        ):
            new_prompt.params.append(param)

    for param in original_chat.params:
        if param.name not in (
            "no_venice_system_prompt",
            "web_search",
            "character",
            "strip_thinking_response",
            "disable_thinking",
        ):
            new_chat.params.append(param)

    @venice.command(name="upscale")
    @click.argument(
        "image_path", type=click.Path(exists=True, dir_okay=False, readable=True)
    )
    @click.option(
        "--scale",
        type=click.FloatRange(1, 4),
        default="2",
        help="Scale factor (between 1 and 4)",
    )
    @click.option(
        "--enhance",
        is_flag=True,
        default=False,
        help="Enhance the image using Venice's image engine",
    )
    @click.option(
        "--enhance-creativity",
        type=click.FloatRange(0.0, 1.0),
        default=None,
        show_default=True,
        help=("Higher values let the enhancement AI change the image more."),
    )
    @click.option(
        "--enhance-prompt",
        type=str,
        default=None,
        show_default=True,
        help="A short descriptive image style prompt to apply during enhancement",
    )
    @click.option(
        "--replication",
        type=click.FloatRange(0.0, 1.0),
        default=None,
        show_default=True,
        help=("How strongly lines and noise in the base image are preserved."),
    )
    @click.option(
        "--output-path",
        "-o",
        type=click.Path(file_okay=True, dir_okay=True, writable=True),
        help="Output path (file or directory)",
    )
    @click.option(
        "--overwrite",
        is_flag=True,
        default=False,
        help="Overwrite existing files",
    )
    def upscale(**kwargs):
        """Upscale an image using Venice API"""
        image_upscale(**kwargs)


@llm.hookimpl
def register_models(register):
    key = llm.get_key("", "venice", "LLM_VENICE_KEY")
    if not key:
        return

    venice_models = llm.user_dir() / "venice_models.json"
    if venice_models.exists():
        models = json.loads(venice_models.read_text())
    else:
        models = refresh_models()

    for model in models:
        model_id = model["id"]
        capabilities = model.get("model_spec", {}).get("capabilities", {})
        if model.get("type") == "text":
            model_instance = VeniceChat(
                model_id=f"venice/{model_id}",
                model_name=model_id,
                api_base="https://api.venice.ai/api/v1",
                can_stream=True,
                vision=capabilities.get("supportsVision", False),
                supports_schema=capabilities.get("supportsResponseSchema", False),
                supports_tools=capabilities.get("supportsFunctionCalling", False),
            )
            model_instance.supports_web_search = capabilities.get(
                "supportsWebSearch", False
            )
            register(model_instance)
        elif model.get("type") == "image":
            register(VeniceImage(model_id=model_id, model_name=model_id))
