import os
import tornado.ioloop
import tornado.web
import uuid

from model.utils import *
from model.sliding_window import *
import asyncio


async def process_file(filename):
    txt = basic_generate(filename)
    parsed_name = uuid.uuid1()
    with open("./parsed/%s.txt" % parsed_name, "w") as file:
        file.write(txt)
    return parsed_name


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        # Set CORS headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")


# Accept file, when finished parsing, return a url for view
class FileUploadHandler(BaseHandler):
    async def post(self):
        files = self.request.files["file"]
        for f in files:
            filename = f["filename"]
            storing = os.path.join("uploads", filename)
            with open(storing, "wb") as out_file:
                out_file.write(f["body"])
            a = SrtFile(storing)
            print(a.content)
            resulting = await process_file(storing)
            # a hypothetical model
            await asyncio.sleep(10)
        self.write(
            {
                "status": "success",
                "message": f"Uploaded {len(files)} files.",
                "url": str(resulting),
            }
        )

    def options(self):
        # No body
        self.set_status(204)
        self.finish()


# gives the view needed
class ViewParagraphHandler(BaseHandler):
    def get(self, id):
        with open("./parsed/%s.txt" % id, "r") as file:
            self.write({
                "paragraph": file.read()
            })


def make_app():
    return tornado.web.Application(
        [
            (r"/upload", FileUploadHandler),
            (r"/paragraph/(.*)", ViewParagraphHandler),
        ],
        debug=True,
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    print("Tornado server started on port 8000 with debug mode enabled.")
    tornado.ioloop.IOLoop.current().start()
