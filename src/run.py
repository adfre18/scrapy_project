# For scrapy framework
import requests
import json
from datetime import datetime

# For webserver
from http.server import BaseHTTPRequestHandler, HTTPServer

# For database
import psycopg2
from sqlalchemy import create_engine
import sqlalchemy as sqlal


class DatabaseConn:
    def __init__(self):
        self.conn = None
        self.db_name = 'exampledb'
        self.db_user = 'docker'
        self.db_pass = 'docker'
        self.db_host = 'database'
        self.db_port = '5432'
        self.db = None
        self.connect()
        self.create_database()

    def connect(self):
        while True:
            print("Trying to connect to database")
            try:
                db_string = 'postgresql://{}:{}@{}:{}/{}'.format(self.db_user, self.db_pass, self.db_host, self.db_port, self.db_name)
                self.db = create_engine(db_string, isolation_level="AUTOCOMMIT")
            except Exception:
                self.db = None
            if self.db is not None:
                break

    def create_database(self):
        # Preparing query to create a database
        sql = '''CREATE database SimpleDB''';
        # Creating a database
        try:
            self.db.execute(sql)
            print("Database created successfully........")
        except Exception:
            # already exists
            pass

        command = "CREATE TABLE estates (estate_title VARCHAR(255) NOT NULL, img_url VARCHAR(255) NOT NULL)"
        try:
            self.db.execute(command)
            print("Table estates created........")
        except Exception:
            # already exists
            pass

    def close(self):
        self.conn.close()

    def insert_info(self, estates):
        delete_statement = "DELETE FROM estates"
        self.db.execute(delete_statement)
        for estate in estates:
            postgres_insert_query = """INSERT INTO estates (estate_title, img_url) VALUES (%s,%s)"""
            record_to_insert = (estate['name'] + ' - ' + estate['locality'], estate['_links']['images'][0]['href'])
            self.db.execute(postgres_insert_query, record_to_insert)

        print("Data inserted")

    def get_info(self):
        connection = self.db.connect()
        metadata = sqlal.MetaData()
        census = sqlal.Table('estates', metadata, autoload=True, autoload_with=self.db)
        query = sqlal.select([census])

        result_proxy = connection.execute(query)
        result_set = result_proxy.fetchall()

        return result_set


db_conn = DatabaseConn()


class ScrapyFramework:

    def get_flat_infos(self):
        dt = datetime.now()
        # getting the timestamp
        ts = datetime.timestamp(dt)
        # formatting to fit the api tms format
        g = float("{:.3f}".format(ts))
        g = str(g).replace(".", "")

        # setting up url
        url = f"https://www.sreality.cz/api/cs/v2/estates?category_main_cb=1&category_type_cb=1&per_page=200&tms={g}"
        # creating request
        response = requests.get(url)
        # loading response
        try:
            estates_full_info = json.loads(response.text, encoding='utf-8')
        except Exception:
            return None
        try:
            estates = estates_full_info['_embedded']['estates']
        except Exception:
            return None

        db_conn.insert_info(estates)


class WebServer(BaseHTTPRequestHandler):
    scrapy_framework = ScrapyFramework()


    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.scrapy_framework.get_flat_infos()
        print("Trying to get data")
        estates = db_conn.get_info()
        self.wfile.write(bytes("<html><head><title>Sreality.cz scrap</title><meta charset='utf-8'><style>h1 {text-align: center;}p {text-align: center;}div {text-align: center;}</style></head>", "utf-8"))
        if estates is None:
            self.wfile.write(bytes(f"<h1>Nebylo možné načíst inzeráty z sreality.cz</h1>", "utf-8"))
        for estate in estates:
            self.wfile.write(bytes(f"<h1>{estate[0]}</h1>", "utf-8"))
            self.wfile.write(bytes(f"<p style='text-align:center;'><img src={estate[1]}></p>", "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))


hostName = "0.0.0.0"
serverPort = 8080

if __name__ == "__main__":

    webServer = HTTPServer((hostName, serverPort), WebServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
