import os
import tornado.ioloop
import tornado.web

from model.utils import *

class FileUploadHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        # Set CORS headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def post(self):
        files = self.request.files["file"]
        for f in files:
            filename = f["filename"]
            storing = os.path.join("uploads", filename)
            with open(storing, "wb") as out_file:
                out_file.write(f["body"])
            a = SrtFile(storing)
            print(a.content)
        self.write({"status": "success", "message": f"Uploaded {len(files)} files."})


    def options(self):
        # No body
        self.set_status(204)
        self.finish()

def make_app():
    return tornado.web.Application([
        (r"/upload", FileUploadHandler),
    ], debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    print("Tornado server started on port 8000 with debug mode enabled.")
    tornado.ioloop.IOLoop.current().start()
