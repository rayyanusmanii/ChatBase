import os
from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, select, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, UTC
from flask_socketio import SocketIO, emit, send, join_room

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "supersecretkey123")
socketio = SocketIO(app, manage_session=False)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///project.db")

# initializes the app
db.init_app(app)

# a model is a class that represents a table. This table is for the signup & login
class User(db.Model): 
    #every attribute is a column
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column() 
# user is a table with 2 columns 


# this table is for the groupchat
class Room(db.Model): 
    id: Mapped[int] = mapped_column(primary_key=True)
    gcnames: Mapped[str] = mapped_column()
    is_dm: Mapped[bool] = mapped_column(default=False)
    
       
# this table is for the messages
class Message(db.Model): 
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column()         
    time_sent: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    # this is a foreign key which links the message to the room
    room_id: Mapped[int] = mapped_column(ForeignKey("room.id"))
    #this is a foreign key which links the message to the user
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship("User")

class RoomMember(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("room.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    hidden_for: Mapped[bool] = mapped_column(default=False) #deleting a chat

# creates all db tables
with app.app_context():
    db.create_all()

# routes to signup page
@app.route("/signup", methods = ["GET", "POST"]) # GET retrieves data (default), POST sends data to server
def signup():
    
    if request.method == "POST":
        username = request.form.get("username")

        # hashing passwords using werkzeug
        password = request.form.get("password")
        hashed_value = generate_password_hash(password)
        
        new_user = User(username = username, password = hashed_value)

        # adding and commiting to db
        db.session.add(new_user)
        db.session.commit()

        # once after signup, user remains logged in
        session ["username"] = username 

        flash("Sign up completed successfully! Welcome!")
        return redirect(url_for("home"))

    return render_template('signup.html')

# routes to login page
@app.route("/login", methods = ["GET", "POST"]) 
def login():
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # finds user in the database
        existing_user = User.query.filter_by(username=username).first()

        # if both user and password are correct, it will redirect to homepage
        if existing_user and check_password_hash(existing_user.password, password):
            session["username"] = username
            return redirect(url_for("home"))
        
        flash("Incorrect e-mail or password.")

    return render_template("signup.html")
            

# routes to homepage
@app.route("/home")
def home():
    # get user object
    user = User.query.filter_by(username=session.get("username")).first()

    #gets all rows for the current user where the rooms aren't hidden
    all_memberships = RoomMember.query.filter_by(user_id=user.id, hidden_for=False).all()

    # get all rooms the user is apart of (only id)
    all_rooms_raw = [Room.query.get(m.room_id) for m in all_memberships]

    #filters list for just the dms
    dm_rooms = [r for r in all_rooms_raw if r and r.is_dm]

    #filters list for just the groups
    gc_rooms = [r for r in all_rooms_raw if r and not r.is_dm]
    return render_template("home.html", dm_rooms=dm_rooms, gc_rooms=gc_rooms, username=session.get("username"))


# routes to the modal that opens when the + button is clicked
@app.route("/create_room", methods= ["GET", "POST"])
def create_room():
    # acquiring room name
    room_name = request.form.get("room_name")

    # updating column in room class with room name
    new_room = Room(gcnames = room_name)

    # adding and commiting to db
    db.session.add(new_room)
    db.session.commit()

    flash("Successfully created!")

    user = User.query.filter_by(username=session.get("username")).first()
    # links user id to new room id so when someone creates a new room, they are part of it by default
    new_roommember = RoomMember(room_id = new_room.id, user_id = user.id)
    db.session.add(new_roommember)
    db.session.commit()

    return redirect(url_for("home"))

# dynamic routing allows for the room_id to be unique to each user when loading message room
# routes to the messages
@app.route("/room/<int:room_id>")
def room(room_id):
    # query that specific room from the database using the id
    room = Room.query.filter_by(id=room_id).first()

    # displays all room names on the sidebar
    user = User.query.filter_by(username=session.get("username")).first()
    memberships = RoomMember.query.filter_by(user_id=user.id, hidden_for=False).all()
    all_rooms_raw = [Room.query.get(m.room_id) for m in memberships]
    dm_rooms = [r for r in all_rooms_raw if r and r.is_dm]
    gc_rooms = [r for r in all_rooms_raw if r and not r.is_dm]

    # displays existing messages in chat area
    existing_messages = Message.query.filter_by(room_id=room_id).all() 
    # id=room_id means you're filtering by the message's own id, 
    # but you want messages where room_id matches. What field should you be filtering on?

    #queries all members for the current room
    all_room_members = [User.query.get(m.user_id) for m in RoomMember.query.filter_by(room_id=room_id).all()]

    print("room_id:", room_id)
    print("all_room_members:", all_room_members)
    return render_template("room.html", room=room, username=session.get("username"), dm_rooms=dm_rooms, gc_rooms=gc_rooms,
                           existing_messages=existing_messages, all_room_members=all_room_members)

# routes to sending the message
@app.route("/room/<int:room_id>/send", methods=["POST"])
def send_message(room_id):
    message = request.form.get("message")

    # user_id expects integer, but we have str
    # after querying the user model and filtering by username, take their user.id 
    user = User.query.filter_by(username=session.get("username")).first()
    
    # message content
    new_message = Message(content = message, room_id = room_id, user_id = user.id)

    db.session.add(new_message)
    db.session.commit()

    return redirect(url_for('room', room_id=room_id))

# when a user sends a message
@socketio.on("message")
def handle_message(data):
    # saving message
    message = data.get("message") #since there is no form, we do not use request.form.get
    room_id = data.get("room_id")

    print("emitting to room:", str(room_id), "type:", type(room_id))

    user = User.query.filter_by(username=data.get("username")).first()
    username = user.username

    now = datetime.now(timezone.utc)

    new_message = Message(content = message, room_id = room_id, user_id = user.id)

    db.session.add(new_message)
    db.session.commit()
    
    # after saving the new message, unhide the room for all members who hid it
    hidden_members = RoomMember.query.filter_by(room_id=room_id, hidden_for=True).all()
    for member in hidden_members:
        member.hidden_for = False
    db.session.commit()
    
    #message will contain the user and their message content
    sent_message = {
        "username": username,
        "content": message
    }

    # broadcasting message
    emit("message", sent_message, to=str(room_id))
    #first argument is what JS listens for, second is what is sent, third is where

# when a user opens the room
@socketio.on('join')
def on_join(data):
    room_id = data.get("room_id")

    print("joining room:", str(room_id), "type:", type(room_id))

    user = User.query.filter_by(username=session.get("username")).first()
    username = user.username

#adds the person to the correct room and str is required since room names must be string because of socketio    
    join_room(str(room_id)) 

# adding members to a room
@app.route("/room/<int:room_id>/add-member", methods=["POST"])
def add_member(room_id):
    username_in_form = request.form.get("username") #retrieves username
    user = User.query.filter_by(username=username_in_form).first() #checks the model to see if a user matches this username
    room = Room.query.filter_by(id=room_id).first()

    if not user: #if user query comes up empty, it flashes an error
        flash("This user does not exist. Try again.")
        return redirect(url_for('room', room_id=room_id))

    #checks if a specific user is already in the room    
    existing = RoomMember.query.filter_by(user_id=user.id, room_id=room_id).first()
    if existing:
        flash("This user is already in the room.")
        return redirect(url_for('room', room_id=room_id))    

    latest_roommember = RoomMember(room_id = room.id, user_id = user.id)
    db.session.add(latest_roommember)
    db.session.commit()

    flash("User added successfully!")

    return redirect(url_for('room', room_id=room_id))
    
# routes to direct messages    
@app.route("/dm/<username>", methods = ["GET"])
def dm(username):
    target_user = User.query.filter_by(username=username).first() #username on left is column in Flask, right is the one from URL
    
    if not target_user:
        flash("User not found.")
        return redirect(url_for("home"))

    current_user = User.query.filter_by(username=session.get("username")).first()
    # the User table is searched for a row that matches what u get from [session.get("username")] 
    # and returned as a user object

    #gets all room ID's the current user is in 
    all_current_user = RoomMember.query.filter_by(user_id=current_user.id).all()

    # loops through the list all_current_user returns and filters just for room_id 
    current_room_ids = []
    for m in all_current_user:
        current_room_ids.append(m.room_id)

    #gets all room ID's the target user is in
    all_target_user = RoomMember.query.filter_by(user_id=target_user.id).all()

     # loops through the list all_target_user returns and filters just for room_id 
    current_target_ids = []
    for m in all_target_user:
        current_target_ids.append(m.room_id)

    #checks for overlap between the current and target user and returns a set
    shared_room_ids = set(current_room_ids) & set(current_target_ids)

    existing_dm = None
    # loop through the set of room ID's that appear on both lists
    # then check if the room exists (r) and if it's a DM and store it in existing_dm
    for room_id in shared_room_ids:
        r = Room.query.get(room_id)
        if r and r.is_dm:
            existing_dm = r
            break
    
    # if existing dm is not none, DM exists so redirecting
    if existing_dm:
        return redirect(url_for('room', room_id=existing_dm.id))
    
    # if existing dm is none, create new room, and add both users and redirect there
    new_room = Room(gcnames=target_user.username, is_dm=True)
    db.session.add(new_room)
    db.session.commit()

    # create 2 room member rows which link both the users to the new room
    user_1 = RoomMember(room_id=new_room.id, user_id= current_user.id)
    user_2 = RoomMember(room_id=new_room.id, user_id= target_user.id)
    db.session.add(user_1)
    db.session.add(user_2)
    db.session.commit()

    return redirect(url_for('room', room_id=new_room.id))
        

#deleting a chat
@app.route("/room/<int:room_id>/hide", methods=["POST"])
def deleting(room_id):
    user = session.get("username")
    user = User.query.filter_by(username=session.get("username")).first()

    #finding user's current roommember
    current_roommember = RoomMember.query.filter_by(room_id=room_id, user_id=user.id).first()

    current_roommember.hidden_for = True #set it to true to hide the room from user
    db.session.commit()
    return redirect(url_for('home'))

# default redirects to login
@app.route("/")
def index():
    return redirect(url_for("login"))

# always ridrects to login page unless for certain instances
@app.before_request
def require_login():
    allowed = ['login', 'signup', 'static'] #these are routes that can access without being logged in
    if request.endpoint not in allowed and not session.get("username"): 
        #checks if the url the user visits is in the allowed constaints and if user is logged in
        return redirect(url_for('login'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)