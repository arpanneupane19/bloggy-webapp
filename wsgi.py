# Copyright ©️ Arpan Neupane 2024. All rights reserved.

from app.main import app, socketio, db

if __name__ == "__main__":
    db.create_all()
    # remove debug=True if you wanna run in production.
    # app.run(debug=True) 
    socketio.run(app, debug=True, port=8080)
