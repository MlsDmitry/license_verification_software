from .app import create_application

app = create_application()

app.run('0.0.0.0', port=8000, debug=True, auto_reload=True)