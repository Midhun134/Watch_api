import os
import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open_new("http://127.0.0.1:8000/admin")

if __name__ == "__main__":
    # Open the browser 1 second after server starts
    Timer(1.0, open_browser).start()

    # Run the Django dev server
    os.system("python manage.py runserver")
