"""
main.py
-------
Single entry point. Run this file to start the app:

    python main.py

It launches the frontend, which in turn calls into the backend
for all real data-fetching and ML work.
"""

from frontend.app import launch_app

if __name__ == "__main__":
    launch_app()
