from flask import Flask, render_template, request, redirect, url_for, session
import database

app = Flask(__name__)
app.secret_key = 'SOME SECRET KEY'


@app.route("/")
def login():
    if 'username' not in session:
        return render_template('login.html')

    else:
        return render_template('newsfeed.html', posts= session['newsfeedPosts'], profile= session['profile'])

@app.route("/home", methods=['GET', 'POST'])
def newsfeed():
    if 'username' not in session:
        username = request.form['username']
        password = request.form['password']
        result = database.login(username, password)

        if result == "Login Successful":
            session['profile'] = database.profile_info(username)
            session['username'] = username
            session['newsfeedPosts'] = database.postsNewsfeed(session['username'])
            return render_template('newsfeed.html', posts=session['newsfeedPosts'], profile=session['profile'])
        elif result == 'incorrect password':
            return render_template('login.html', info="Wrong Password")
        elif result == 'user does not exist':
            return render_template('login.html', info="Account Not Found")
    else:
        return render_template('newsfeed.html', posts=session['newsfeedPosts'], profile=session['profile'])


@app.route("/outgoingReq")
def outgoingReq():
    if 'username' in session:
        username = session['username']
        session['outReq'] = database.outInfo(username)
        return render_template('outgoingReq.html', profiles=session['outReq'])

@app.route("/incomingReq")
def incomingReq():
    if 'username' in session:
        username = session['username']
        session['incReq'] = database.inInfo(username)
        return render_template('incomingReq.html', profiles=session['incReq'])


@app.route("/logout")
def logout():
    session.clear()
    return render_template('logout_confirmation.html')

@app.route("/hardRefresh")
def hardRefresh():
    if 'username' in session:
        session['profile'] = database.profile_info(session['username'])
        session['profilePosts'] = database.postsNewsfeed(session['username'])
        session['newsfeedPosts'] = database.postsNewsfeed(session['username'])
        session['suggestions'] = database.suggestions(session['username'])
        session['friends'] = database.frineds(session['username'])
        return redirect("/")

    else:
        return redirect("/")


@app.route("/signup_confirmation", methods=['GET', 'POST'])
def signin_confirmation():
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    email = request.form['email']
    bio = request.form['bio']
    location = request.form['location']
    gender = request.form['gender']

    database.createProfile(username, password, name, email, bio, location, gender)
    return render_template('signup_confirmation.html')

@app.route("/post_confirmation", methods=['GET', 'POST'])
def post_confirmation():
    text = request.form['text']
    author_username = session['username']
    feedback = database.createPost(text, author_username)

    if feedback == "post created":
        return render_template('post_confirmation.html')
    else:
        return "something went wrong"


@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route('/profile')
def profilepage():
    if 'username' in session:
        session['profilePosts'] = database.postsProfile(session['username'])
        mine = True
        return render_template('profile.html', posts=session['profilePosts'], profile=session['profile'], mine=mine)

@app.route('/search')
def search():
    return render_template('search_accounts.html')

@app.route('/searchResult', methods=['GET', 'POST'])
def searchresult():
    if 'username' in session:
        searched_username = request.form['query']
        allUserName = database.allUserName()
        if searched_username in allUserName:
            return redirect('/profile/' + searched_username)
        else:
            return render_template('profile_not_found.html')

@app.route('/acceptreq/<username>')
def acceptreq(username):
    if 'username' in session:
        feedbacck = database.acceptReq(username, session['username'])
        session['friends'] = database.frineds(session['username'])
        session['suggestions'] = database.suggestions(session['username'])
        session['newsfeedPosts'] = database.postsNewsfeed(session['username'])
        if feedbacck == "Accepted":
            return redirect('/profile/' + username)
        else:
            return 'something went wrong'

@app.route("/unfriend/<username>")
def unfriend(username):
    if 'username' in session:
        feedback = database.unfriend(username, session['username'])
        session['friends'] = database.frineds(session['username'])
        session['suggestions'] = database.suggestions(session['username'])
        session['newsfeedPosts'] = database.postsNewsfeed(session['username'])
        if feedback == "done":
            return redirect('/profile/' + username)
        else:
            return 'something went wrong'

@app.route("/editProfileInfo")
def editProfileInfo():
    return render_template("edit_profile_info.html", profile=session['profile'])

@app.route("/update-profile", methods=['GET', 'POST'])
def updateProfile():
    if 'username' in session:
        username = session['username']
        password = request.form['current-password']
        result = database.login(username, password)
        if result == "Login Successful":
            name = request.form['name']
            location = request.form['location']
            bio = request.form['bio']
            email = request.form['email']
            newpassword = request.form['password']
            feedback = database.updateProfile(username, name, location, bio, email, newpassword)
            session['newsfeedPosts'] = database.postsNewsfeed(session['username'])
            session['friends'] = database.frineds(session['username'])
            session['suggestions'] = database.suggestions(session['username'])
            session['profilePosts'] = database.postsProfile(session['username'])
            session['profile'] = database.profile_info(session['username'])
            if feedback == "succesfully updated profile":
                return render_template("profileupdateconfirmation.html")
            else:
                return "something went wrong"


@app.route("/authenticateDelete", methods=['GET', 'POST'])
def authenticateDelete():
    if 'username' in session:
        username = session['username']
        password = request.form['password']
        result = database.login(username, password)
        if result == "Login Successful":
            feedback = database.deleteAccounts(username)
            if feedback == "Account deleted":
                session.clear()
                return render_template("deletionSuccessful.html")
            else:
                return "something went wrong"
        else:
            return " worng password"

@app.route("/deleteAccount")
def deleteAccount():
    if 'username' in session:
        username = session['username']
        return render_template("deleteCOnfirmation.html", username=username)


@app.route("/cancelreq/<username>")
def cancelreq(username):
    if 'username' in session:
        feedback = database.cancelReq(username, session['username'])
        session['friends'] = database.frineds(session['username'])
        session['suggestions'] = database.suggestions(session['username'])
        session['newsfeedPosts'] = database.postsNewsfeed(session['username'])
        if feedback == "Cancelled":
            return redirect('/profile/' + username)
        else:
            return 'something went wrong'

@app.route("/like/<post_id>", methods=['GET', 'POST'])
def like(post_id):
    database.incLike(post_id, session['username'])
    session['profilePosts'] = database.postsProfile(session['username'])
    session['newsfeedPosts'] = database.postsNewsfeed(session['username'])
    temp_arr = []
    for post in session['profilePosts']:
        temp_arr.append(post['post_id'])
    if int(post_id) not in temp_arr:
        return redirect(url_for('newsfeed'))
    else:
        return redirect(url_for('profilepage'))


@app.route("/profile/addnewfriend/<username>")
def addnewfriend(username):
    feedback = database.addPendingreq(username, session['username'])
    if feedback == 'succesfully added pending request':
        return redirect('/profile/' + username)
    else:
        return 'failed'

@app.route('/profile/<username>')
def profilepage1(username):
    session['viewProfile'] = database.profile_info(username)
    session['viewProfilePosts'] = database.postsProfile(username)
    if username == session['username']:
        mine = True
    else:
        mine = False
    session['isFriend'] = False
    for i in session['friends']:
        if i['username'] == username:
            session['isFriend'] = True
            break
    isRequested = database.isReq(username, session['username'])
    isRecieved = database.isRec(username, session['username'])

    return render_template("profile.html", posts=session['viewProfilePosts'], profile=session['viewProfile'], mine=mine, isFriend=session['isFriend'], isRecieved=isRecieved, isRequested=isRequested)

@app.route('/postcomments/<post_id>')
def postcomments(post_id):
    post_id = int(post_id)
    post = database.findPost(post_id)
    return render_template('comments.html', comments=post['comments'] , post=post, username=session['username'])

@app.route("/deletepost/<post_id>")
def deletepost(post_id):
    post_id = int(post_id)
    feedback = database.deletepost(post_id)
    if feedback == "post deleted":
        return render_template("post_deletion_confirmation.html")

    else:
        return "something went wrong"

@app.route("/comments/<post_id>/new", methods=['GET', 'POST'])
def comments(post_id):
    text = request.form['comm']
    commenter = session['username']
    comment_on = post_id
    feedback1 = database.createComment(commenter, comment_on, text)
    if feedback1 == "comment created":
        post = database.findPost(post_id)
        session['profilePosts'] = database.postsProfile(session['username'])
        session['newsfeedPosts'] = database.postsNewsfeed(session['username'])
        return render_template('comments.html', comments=post['comments'] , post=post)
    else:
        return "something went wrong"


@app.route('/friends')
def friendspage():
    if 'username' in session:
        session['friends'] = database.frineds(session['username'])
        session['suggestions'] = database.suggestions(session['username'])
        return render_template('friends.html', friends= session['friends'], profiles = session['suggestions'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

