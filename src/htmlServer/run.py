# Python 3 server example
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import sys
import os
import re
print(os.path.abspath(os.getcwd()))
pattern = re.compile("Scrapy_project")
res = re.search(pattern, str(os.path.abspath(os.getcwd())))
if res:
    sys.path.insert(0, str(os.path.abspath(os.getcwd())[:res.regs[0][1]]))

from src.scrapy.main import SimpleScrapyFramework

hostName = "127.0.0.1"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title><meta charset='utf-8'><style>h1 {text-align: center;}p {text-align: center;}div {text-align: center;}</style></head>", "utf-8"))
        for output_pair in output_pairs:
            self.wfile.write(bytes(f"<h1>{output_pair[0]}</h1>", "utf-8"))
            self.wfile.write(bytes(f"<p style='text-align:center;'><img src={output_pair[1]}></p>", "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            #self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))


if __name__ == "__main__":
    scrapy_framework = SimpleScrapyFramework()
    output_pairs = scrapy_framework.scrape_url()
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
