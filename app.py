import os

import appdata
import webview
import threading
import sys

import porter
app = porter.create_app()

def start_flask(debug=False):
    app.run(debug=debug, use_reloader=False, port=5000)

def start_webview(debug=False):
    link = 'http://127.0.0.1:5000'
    if debug:
        link += '/debug'

    window = webview.create_window('Porter', link, width=860, height=840, on_top=True)
    app.config["WEBVIEW_WINDOW"] = window

    webview.start()

def main(headless=False, debug=False, reset=False):
    if reset:
        app_paths = appdata.AppDataPaths("Pyrite Asset Porter")
        app_paths.setup()

        # Remove config file
        if os.path.exists(app_paths.config_path):
            os.remove(app_paths.config_path)

        # Remove groups file
        groups_file = os.path.join(app_paths.app_data_path, 'groups.json')
        if os.path.exists(groups_file):
            os.remove(groups_file)

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
        debug='--debug' in sys.argv,
        reset='--reset' in sys.argv
    )
