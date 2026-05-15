import os

import webview
import threading
import sys

import porter

def start_flask():
    app = porter.create_app()
    app.run(debug=True, use_reloader=False, port=5000)

def start_webview():
    # Create a webview window
    webview.create_window('Porter', 'http://127.0.0.1:5000', width=1280, height=720)
    webview.start()

def main(headless=False):
    if headless:
        # Start the Flask app in the main thread
        start_flask()
        return
    
    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Start the webview in the main thread
    start_webview()

if __name__ == '__main__':
    main(headless='--headless' in sys.argv)
