from __future__ import annotations

import os
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class RangeRequestHandler(SimpleHTTPRequestHandler):
    range_header = re.compile(r"bytes=(\d*)-(\d*)$")

    def send_head(self):
        path = self.translate_path(self.path)

        if os.path.isdir(path):
            return super().send_head()

        try:
            file = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None

        size = os.fstat(file.fileno()).st_size
        start = 0
        end = size - 1
        status = 200

        header = self.headers.get("Range")
        if header:
            match = self.range_header.fullmatch(header.strip())
            if match:
                start_text, end_text = match.groups()
                if start_text:
                    start = int(start_text)
                if end_text:
                    end = int(end_text)
                if start_text == "" and end_text:
                    length = int(end_text)
                    start = max(size - length, 0)
                    end = size - 1
                if start > end or start >= size:
                    self.send_error(416, "Requested Range Not Satisfiable")
                    file.close()
                    return None
                end = min(end, size - 1)
                status = 206

        content_length = (end - start) + 1
        content_type = self.guess_type(path)

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(content_length))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Last-Modified", self.date_time_string(os.path.getmtime(path)))
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()

        self.range = (start, end)
        return file

    def copyfile(self, source, outputfile):
        range_values = getattr(self, "range", None)
        if not range_values:
            return super().copyfile(source, outputfile)

        start, end = range_values
        remaining = (end - start) + 1
        source.seek(start)

        while remaining > 0:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)


if __name__ == "__main__":
    port = 8001
    server = ThreadingHTTPServer(("127.0.0.1", port), RangeRequestHandler)
    print(f"Serving with range support on http://localhost:{port}")
    server.serve_forever()
