def create_app():
    app = Flask(__name__)
    @app.route("/")
    def hello():
        return "Hello from hello_world package!"
    return app
