import os

import webview
import threading
import sys

import porter

def start_flask(debug=False):
    app = porter.create_app()
    app.run(debug=debug, use_reloader=False, port=5000)

def start_webview(debug=False):
    link = 'http://127.0.0.1:5000'
    if debug:
        link += '/debug'

    webview.create_window('Porter', link, width=1280, height=720)
    webview.start()

def main(headless=False, debug=False):
    if headless:
        # Start the Flask app in the main thread
        start_flask(debug=debug)
        return
    
    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=start_flask, kwargs={'debug': debug})
    flask_thread.daemon = True
    flask_thread.start()

    # Start the webview in the main thread
    start_webview(debug=debug)

if __name__ == '__main__':
    main(
        headless='--headless' in sys.argv,
        debug='--debug' in sys.argv
    )
