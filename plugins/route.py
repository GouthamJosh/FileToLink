# Fully Updated Server Code (Supports /secureHashID/filename)

import re, math, logging, secrets, mimetypes
from info import *
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from TechVJ.bot import multi_clients, work_loads
from TechVJ.server.exceptions import FIleNotFound, InvalidHash
from TechVJ.util.custom_dl import ByteStreamer
from TechVJ.util.render_template import render_page

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("File 2 Link ⚡")

# -------------------------------------------------
# EXTRACT ID + HASH (New Version)
# Supports:
#   /AgADzh224/filename.mkv
#   /AgADzh224
#   /224/filename?hash=AgADzh
#   /224?hash=AgADzh
# -------------------------------------------------

def extract_id_hash(path, query_hash):
    # Clean encoded parts
    try:
        path = path.encode('latin1', 'replace').decode('utf-8', 'ignore')
    except:
        pass

    clean = path.split("/")[0]  # always take before first slash

    # Case 1: /AgADzh224 (with or without filename)
    direct = re.match(r"([A-Za-z0-9_-]{6})(d+)", clean)
    if direct:
        return int(direct.group(2)), direct.group(1)

    # Case 2: /224/filename + hash in query
    if clean.isdigit():
        return int(clean), query_hash

    # Fallback: detect first number as ID
    digits = re.findall(r"d+", clean)
    if digits:
        return int(digits[0]), query_hash

    raise FIleNotFound("Invalid Path Format")

# -------------------------------------------------
# WATCH ROUTE
# -------------------------------------------------

@routes.get(r"/watch/{path:S+}", allow_head=True)
async def watch_handler(request: web.Request):
    try:
        p = request.match_info["path"]
        qh = request.rel_url.query.get("hash")
        file_id, secure_hash = extract_id_hash(p, qh)
        return web.Response(text=await render_page(file_id, secure_hash), content_type='text/html')
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except Exception as e:
        logging.critical(str(e))
        raise web.HTTPInternalServerError(text=str(e))

# -------------------------------------------------
# STREAM ROUTE
# -------------------------------------------------

@routes.get(r"/{path:S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        p = request.match_info["path"]
        qh = request.rel_url.query.get("hash")
        file_id, secure_hash = extract_id_hash(p, qh)
        return await media_streamer(request, file_id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except Exception as e:
        logging.critical(str(e))
        raise web.HTTPInternalServerError(text=str(e))

class_cache = {}

# -------------------------------------------------
# MEDIA STREAMER
# -------------------------------------------------

async def media_streamer(request: web.Request, id: int, secure_hash: str):
    range_header = request.headers.get("Range", 0)

    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]

    if MULTI_CLIENT:
        logging.info(f"Client {index} serving {request.remote}")

    # Cache Telegram session
    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
    else:
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect

    file_id = await tg_connect.get_file_properties(id)

    # HASH CHECK
    if file_id.unique_id[:6] != secure_hash:
        raise InvalidHash

    file_size = file_id.file_size

    # RANGE HANDLING
    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if from_bytes < 0 or until_bytes < from_bytes or until_bytes > file_size:
        return web.Response(status=416, body="416: Range not satisfiable",
                            headers={"Content-Range": f"bytes */{file_size}"})

    chunk_size = 1024 * 1024
    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)

    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )

    mime_type = file_id.mime_type or "application/octet-stream"
    file_name = file_id.file_name or f"{secrets.token_hex(4)}.bin"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": mime_type,
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )
