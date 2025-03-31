from flask import Flask
from routes.logger import logger 

app = Flask(__name__)

# Register the recommender blueprint
app.register_blueprint(logger, url_prefix="/logger")

if __name__ == '__main__':
    app.run(debug=True)