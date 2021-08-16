from .app import create_application

app = create_application()
app.run('0.0.0.0', port=31563, debug=True, workers=1, hot_reload=True)
