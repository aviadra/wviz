import argparse
import http.server
import os
import imghdr
import subprocess
import sys
import os


class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_PUT(self):
        path = self.translate_path(self.path)
        if path.endswith('/'):
            self.send_response(405, "Method Not Allowed")
            self.wfile.write("PUT not allowed on a directory\n".encode())
            return
        else:
            try:
                os.makedirs(os.path.dirname(path))
            except FileExistsError: pass
            length = int(self.headers['Content-Length'])
            with open(path, 'wb') as f:
                f.write(self.rfile.read(length))

            image_type = imghdr.what(f.name)
            if not image_type:
                print("error")
                ## If file exists, delete it ##
                if os.path.isfile(f.name):
                    os.remove(f.name)
                    print("deleted file %s" % f.name)
                else:    ## Show an error ##
                    print("Error: %s file not found" % f.name)
                self.send_response(405, "File type Rejected")
                self.end_headers()
            else:
                print(image_type)
                dirname = os.path.dirname(__file__)
                facedetectPath = os.path.join(dirname, "facedetect", "facedetect")
                faceDetect = subprocess.run(["python", facedetectPath, f.name, "--biggest"], capture_output=True)
                self.send_response(201, "Created")
                self.end_headers()
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', '-b', default='', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()

    http.server.test(HandlerClass=HTTPRequestHandler, port=args.port, bind=args.bind)