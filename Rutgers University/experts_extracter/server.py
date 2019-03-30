# server.py
import subprocess
import csv
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    """
    Run spider in another process and store items in file. Simply issue command:

    > scrapy crawl dmoz -o "output.json"

    wait for  this command to finish, and read output.json to client.
    """
    spider_name = "dmoz"
    # subprocess.check_output(['scrapy', 'crawl', "expert_extract_spider"])
    with open("Rutgers University.csv") as items_file:
        return items_file.read()
if __name__ == '__main__':
    app.run(debug=True)