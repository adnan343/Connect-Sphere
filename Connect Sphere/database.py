from sqlalchemy import create_engine, text
import datetime

dbConn = "mysql+pymysql://root:@localhost/connect_sphere2.0?charset=utf8mb4"
engine = create_engine(dbConn)



def login(username, password):
    with engine.connect() as conn:
        result = conn.execute(text("select password from user where username = '%s'" % username))
        result = result.fetchone()
        try:
            if result[0] == password:
                return "Login Successful"
            else:
                return 'incorrect password'
        except:
            return 'user does not exist'

def createPost(text1, author_username):
    try:
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO Posts (Posted_At, Text, Author_Username) VALUES (:postedAt, :text, :authorUsername)"), {"postedAt": datetime.datetime.now(), "text": text1, "authorUsername": author_username})
            conn.commit()
            return "post created"

    except:
        return "something went wrong"

def createProfile(username, password, name, email, bio, location, gender):
    with engine.connect() as conn:
        try:
            conn.execute(
                text(
                    "INSERT INTO User (Username, Name, Gender, Location, Bio, Password, Email, joined) VALUES (:username, :name, :gender, :location, :bio, :password, :email, :joined)"),
                {"username": username, "name": name, "gender": gender, "location": location, "bio": bio,
                 "password": password, "email": email, "joined": datetime.datetime.now()}
            )
            conn.commit()
            return "Profile created successfully"
        except:
            return "something went wrong"


def frineds(username):
    with engine.connect() as conn:
        result = conn.execute(text("select user1 from friendship where user2 = '%s'" % username))
        arr = []
        for row in result:
            dict1 = {"username": row[0]}
            name = conn.execute(text("select name from user where username = '%s'" % row[0])).fetchone()
            dict1["name"] = name[0]
            arr.append(dict1)
        result1 = conn.execute(text("select user2 from friendship where user1 = '%s'" % username))
        for row in result1:
            dict1 = {"username": row[0]}
            name = conn.execute(text("select name from user where username = '%s'" % row[0])).fetchone()
            dict1["name"] = name[0]
            arr.append(dict1)

        return arr

def outInfo(username):
    with engine.connect() as conn:
        result = reqList(username)
        arr = []
        for row in result:
            dict1 = {"username": row}
            name = conn.execute(text("select name from user where username = '%s'" % row)).fetchone()
            dict1["name"] = name[0]
            arr.append(dict1)

    return arr

def acceptReq(sender, receiver):
    with engine.connect() as conn:
        try:
            conn.execute(text("DELETE FROM pending_requests WHERE `pending_requests`.`sender` = :sender AND `pending_requests`.`receiver` = :receiver"), {"sender": sender, "receiver": receiver})
            conn.commit()
            conn.execute(text("INSERT INTO `friendship` (`User1`, `User2`, `Since`) VALUES (:user1, :user2, :since)"), {"user1": sender, "user2": receiver, "since": datetime.datetime.now()})
            conn.commit()
            return "Accepted"
        except:
            return "something went wrong"

def deleteAccounts(username):
    try:
        with engine.connect() as conn:
            conn.execute(text("delete from `user` where username = '%s'" % username))
            conn.commit()
            return "Account deleted"

    except:
        return "something went wrong"


def deletepost(postID):
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM posts WHERE `posts`.`Post_ID` = :postID"), {"postID": postID})
            conn.commit()
            return "post deleted"
    except:
        return "something went wrong"


def cancelReq(receiver ,sender):
    with engine.connect() as conn:
        try:
            conn.execute(text("DELETE FROM pending_requests WHERE `pending_requests`.`sender` = :sender AND `pending_requests`.`receiver` = :receiver"), {"sender": sender, "receiver": receiver})
            conn.commit()
            return "Cancelled"

        except:
            return "something went wrong"

def unfriend(username1, username2):
    with engine.connect() as conn:
        try:
            conn.execute(text("DELETE FROM friendship WHERE `friendship`.`User1` = :username1 AND `friendship`.`User2` = :username2"), {"username1": username1, "username2": username2})
            conn.commit()
            conn.execute(text("DELETE FROM friendship WHERE `friendship`.`User1` = :username1 AND `friendship`.`User2` = :username2"), {"username1": username2, "username2": username1})
            conn.commit()
            return "done"
        except:
            return "something went wrong"

def inInfo(username):
    with engine.connect() as conn:
        result = recList(username)
        arr = []
        for row in result:
            dict1 = {"username": row}
            name = conn.execute(text("select name from user where username = '%s'" % row)).fetchone()
            dict1["name"] = name[0]
            arr.append(dict1)

    return arr

def suggestions(username):
    with engine.connect() as conn:
        frnd = frineds(username)
        location = conn.execute(text("select Location from User where username = '%s'" % username)).fetchone()
        location = location[0]
        result = conn.execute(text("select username, name from user where location = '%s'" % location))
        result = result.all()
        reqout = reqList(username)
        reqin = recList(username)
        arr1 = []
        for i in result:
            dict1 = {"username": i[0], "name": i[1]}
            if dict1 not in frnd and i[0] != username and i[0] not in reqin and i[0] not in reqout:
                arr1.append(dict1)

    return arr1

def profile_info(username):
    with engine.connect() as conn:
        result = conn.execute(text("select name, gender, location, bio, joined, email from user where username = '%s'" % username))
        result = list(result.fetchone())
        resultDict = {"username": username, "name": result[0], "gender": result[1], "location": result[2], "bio": result[3], "joined": result[4], "email": result[5]}
        return resultDict


def postsNewsfeed(username):
    given_username = username

    with engine.connect() as conn:
        result = conn.execute(text('''
            SELECT p.*
            FROM Posts p
            JOIN Friendship f
            ON (p.Author_Username = f.User1 OR p.Author_Username = f.User2)
            WHERE (f.User1 = :given_username OR f.User2 = :given_username)
            AND p.Author_Username != :given_username order by Posted_At desc
        '''), {'given_username': given_username})

        result = result.all()
        arr = []
        for i in result:
            dict1 = {'text': i[2], 'authorusr': i[4], 'duration': i[1], 'post_id': i[0]}
            name = conn.execute(text("select Name from User where username = '%s'" % i[4])).fetchone()
            dict1['author']= name[0]
            likes = conn.execute(text("select * from reactions_on_posts where post_id = :post_id and reaction = :reaction"), {'post_id': i[0], 'reaction': "Like"})
            likes = len(likes.all())
            dict1['likes'] = likes
            comments = conn.execute(text("select * from comments where comment_on = :post_id"), {'post_id': i[0]})
            comments = comments.all()
            commentsNum = len(comments)
            dict1['commentsNo'] = commentsNum
            arr1 = []
            for j in comments:
                dict2 = {"text": j[2], "commenter": j[4]}
                arr1.append(dict2)
            dict1['comments'] = arr1
            arr.append(dict1)
        return arr

def incLike(post_id, username):
    try:
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO `reactions_on_posts` (`Post_ID`, `Username_of_Reactor`, `Reaction`) VALUES (:post_id, :username, :reaction)"), {'post_id': post_id, 'username': username, 'reaction': "Like"})
            conn.commit()
            print("yee")
            return "post created"
    except:
        print("nooo")
        with engine.connect() as conn:
            conn.execute(text(
                "DELETE FROM `reactions_on_posts` WHERE `reactions_on_posts`.`Post_ID` = :post_id AND `reactions_on_posts`.`Username_of_Reactor` = :username"),
                         {'post_id': post_id, 'username': username})
            conn.commit()



def postsProfile(username):
    given_username = username
    with engine.connect() as conn:
        result = conn.execute(text("select * from posts where author_username = '%s' order by Posted_At DESC" % given_username))
        result = result.all()
        arr = []
        for i in result:
            dict1 = {'text': i[2], 'authorusr': i[4], 'duration': i[1], 'post_id': i[0]}
            name = conn.execute(text("select Name from User where username = '%s'" % i[4])).fetchone()
            dict1['author'] = name[0]
            likes = conn.execute(
                text("select * from reactions_on_posts where post_id = :post_id and reaction = :reaction"),
                {'post_id': i[0], 'reaction': "Like"})
            likes = len(likes.all())
            dict1['likes'] = likes
            comments = conn.execute(text("select * from comments where comment_on = :post_id"), {'post_id': i[0]})
            comments = comments.all()
            commentsNum = len(comments)
            dict1['commentsNo'] = commentsNum
            arr1 = []
            for j in comments:
                dict2 = {"text": j[2], "commenter": j[4]}
                arr1.append(dict2)
            dict1['comments'] = arr1
            arr.append(dict1)
        return arr

def findPost(post_id):
    try:
        with engine.connect() as conn:
            i = conn.execute(text("select * from posts where post_id = :post_id"), {'post_id': post_id})
            i = i.all()
            i= i[0]
            dict1 = {'text': i[2], 'authorusr': i[4], 'duration': i[1], 'post_id': i[0]}
            name = conn.execute(text("select Name from User where username = '%s'" % i[4])).fetchone()
            dict1['author'] = name[0]
            likes = conn.execute(
                text("select * from reactions_on_posts where post_id = :post_id and reaction = :reaction"),
                {'post_id': i[0], 'reaction': "Like"})
            likes = len(likes.all())
            dict1['likes'] = likes
            comments = conn.execute(text("select * from comments where comment_on = :post_id"), {'post_id': i[0]})
            comments = comments.all()
            commentsNum = len(comments)
            dict1['commentsNo'] = commentsNum
            arr1 = []
            for j in comments:
                dict2 = {"comment_id": j[0] ,"text": j[2], "commenter": j[4]}
                arr1.append(dict2)
            dict1['comments'] = arr1
            return dict1
    except:
        return "post not found"


def createComment(commenter, comment_on, text1):
    try:
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO Comments (Posted_At, Text, Comment_On, Commenter) VALUES (:postedAt, :text, :comment_on, :commenter)"), {"postedAt": datetime.datetime.now(), "text": text1, "comment_on": comment_on, "commenter": commenter})
            conn.commit()
            return "comment created"
    except:
        return "something went wrong"

def allUserName():
    with engine.connect() as conn:
        result = conn.execute(text("select Username from User order by Username desc"))
        result = result.all()
        arr = []
        for i in result:
            arr.append(i[0])
        return arr


def addPendingreq(receiver, sender):
    with engine.connect() as conn:
        try:
            conn.execute(text("Insert into pending_requests (sender, receiver) values (:sender, :receiver)"), {'sender': sender, 'receiver': receiver})
            conn.commit()
            return 'succesfully added pending request'
        except:
            return "something went wrong"

def isReq(receiver, sender):
    with engine.connect() as conn:
        try:
            result = conn.execute(text("select * from pending_requests where receiver = :receiver and sender = :sender"), {'receiver': receiver, 'sender': sender})
            result = result.all()
            if len(result) == 0:
                return False
            else:
                return True
        except:
            return 'something went wrong'


def isRec(sender, receiver):
    with engine.connect() as conn:
        try:
            result = conn.execute(text("select * from pending_requests where receiver = :receiver and sender = :sender"), {'receiver': receiver, 'sender': sender})
            result = result.all()
            if len(result) == 0:
                return False
            else:
                return True
        except:
            return 'something went wrong'


def reqList(username):
    with engine.connect() as conn:
        try:
            result = conn.execute(text("select receiver from pending_requests where sender = :username"), {'username': username})
            result = result.all()
            arr = []
            for i in result:
                arr.append(i[0])
            return arr
        except:
            return "something went wrong"

def recList(username):
    with engine.connect() as conn:
        try:
            result = conn.execute(text("select sender from pending_requests where receiver = :username"), {'username': username})
            result = result.all()
            arr = []
            for i in result:
                arr.append(i[0])
            return arr
        except:
            return "something went wrong"

def updateProfile(username, name, location, bio, email, newpassword):
    with engine.connect() as conn:
        try:
            conn.execute(text("UPDATE `user` SET `Name` = :name, location = :location, bio = :bio, email = :email, password = :password WHERE `user`.`Username` = :username"), {'name': name, 'location': location, 'bio': bio, 'email': email, 'password': newpassword, 'username': username})
            conn.commit()
            return 'succesfully updated profile'

        except:
            return "something went wrong"



