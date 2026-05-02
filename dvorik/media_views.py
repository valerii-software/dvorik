"""Range-aware MEDIA_ROOT serve view for development.

Django's `django.views.static.serve` ignores the Range header and always
returns the whole file with status 200, so HTML5 <video> can't scrub.
This view returns 206 Partial Content for valid Range requests.
"""

import mimetypes
import os
import re
from pathlib import Path
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
)


_RANGE_RE = re.compile(r'bytes=(\d*)-(\d*)$')


def _resolve(path):
    root = Path(settings.MEDIA_ROOT).resolve()
    full = (root / path).resolve()
    if not str(full).startswith(str(root)):
        raise Http404
    if not full.is_file():
        raise Http404
    return full


def serve_media(request, path):
    full = _resolve(path)
    size = full.stat().st_size
    content_type, _ = mimetypes.guess_type(str(full))
    content_type = content_type or 'application/octet-stream'

    range_header = request.headers.get('Range', '')
    if range_header:
        m = _RANGE_RE.match(range_header.strip())
        if not m:
            return HttpResponseBadRequest('Invalid Range header')
        start_s, end_s = m.group(1), m.group(2)
        if start_s == '' and end_s == '':
            return HttpResponseBadRequest('Invalid Range header')
        if start_s == '':
            length = int(end_s)
            start = max(size - length, 0)
            end = size - 1
        else:
            start = int(start_s)
            end = int(end_s) if end_s else size - 1
        if start > end or start >= size:
            resp = HttpResponse(status=416)
            resp['Content-Range'] = f'bytes */{size}'
            return resp
        end = min(end, size - 1)
        length = end - start + 1
        f = open(full, 'rb')
        f.seek(start)
        resp = HttpResponse(
            FileWrapper(f, blksize=8192 * 8),
            status=206,
            content_type=content_type,
        )
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = f'bytes {start}-{end}/{size}'
        resp['Accept-Ranges'] = 'bytes'
        # Truncate the wrapper to `length` bytes by wrapping in a generator
        def streamer():
            remaining = length
            while remaining > 0:
                chunk = f.read(min(8192 * 8, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk
            f.close()
        resp.streaming_content = streamer()
        return resp

    response = FileResponse(open(full, 'rb'), content_type=content_type)
    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = str(size)
    return response
