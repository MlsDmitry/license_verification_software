from .app import create_application

app = create_application()
app.run('0.0.0.0', port=31563, debug=False, workers=1)
