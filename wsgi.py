# Copyright ©️ Arpan Neupane 2022-23. All rights reserved.

from app.main import app, socketio, db

if __name__ == "__main__":
    db.create_all()
    app.run()
