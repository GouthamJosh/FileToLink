import re, math, logging, secrets, mimetypes, time

from info import *
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine

from TechVJ.bot import multi_clients, work_loads, TechVJBot
from TechVJ.server.exceptions import FIleNotFound, InvalidHash
from TechVJ import StartTime, __version__
from TechVJ.util.custom_dl import ByteStreamer
from TechVJ.util.time_format import get_readable_time
from TechVJ.util.render_template import render_page

routes = web.RouteTableDef()

# ----------------- ROOT -----------------
@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("File 2 Link ⚡")

# --------------- WATCH PAGE ---------------
@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def watch_page_handler(request: web.Request):
    try:
        path = request.match_info["path"]

        # Extract secure hash + ID
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            try:
                id = int(re.search(r"(\d+)", path).group(1))
            except AttributeError:
                raise FIleNotFound("Invalid path format: ID not found.")  # Fixed: Removed keyword argument
            secure_hash = request.rel_url.query.get("hash")

        return web.Response(
            text=await render_page(id, secure_hash),
            content_type='text/html'
        )

    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

# ---------------- MEDIA STREAM -----------------
@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]

        # Extract hash + ID
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            try:
                id = int(re.search(r"(\d+)", path).group(1))
            except AttributeError:
                raise FIleNotFound("Invalid path format: ID not found.")  # Fixed: Removed keyword argument
            secure_hash = request.rel_url.query.get("hash")

        return await media_streamer(request, id, secure_hash)

    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

# Cache ByteStreamer objects per-client
class_cache = {}


# ---------------- CORE STREAMER ----------------
async def media_streamer(request: web.Request, id: int, secure_hash: str):

    # Whether client sent Range header
    range_requested = "Range" in request.headers

    # Select fastest client
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]

    if MULTI_CLIENT:
        logging.info(f"Client {index} serving {request.remote}")

    # Cache ByteStreamer object
    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer for client {index}")
    else:
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
        logging.debug(f"Created new ByteStreamer for client {index}")

    # Fetch Telegram file info
    file_id = await tg_connect.get_file_properties(id)

    # Validate hash
    if file_id.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for ID {id}")
        raise InvalidHash

    file_size = file_id.file_size

    # ---------------- RANGE PROCESSING ----------------
    from_bytes = request.http_range.start or 0
    until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"}
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)

    # Create streaming generator
    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )

    # ---------------- FILE NAME FIX (THE IMPORTANT PART) ----------------
    mime_type = file_id.mime_type
    file_name = file_id.file_name  # ORIGINAL TG FILE NAME

    # If Telegram did not store a name, generate safe fallback
    if not file_name:
        if mime_type and "/" in mime_type:
            ext = mime_type.split("/")[1]
            file_name = f"{secrets.token_hex(2)}.{ext}"
        else:
            file_name = f"{secrets.token_hex(2)}.unknown"

    # If no MIME type, guess using file name
    if not mime_type:
        if file_name:
            mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
        else:
            mime_type = "application/octet-stream"

    disposition = "attachment"

    # ---------------- RETURN STREAM ----------------
    return web.Response(
        status=206 if range_requested else 200,
        body=body,
        headers={
            "Content-Type": mime_type,
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes"
        }
    )
