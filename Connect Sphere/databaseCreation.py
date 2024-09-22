from sqlalchemy import create_engine, text

dbConn = "mysql+pymysql://root:@localhost/connect_sphere2.0?charset=utf8mb4"
engine = create_engine(dbConn)


def initialize_database():
    with engine.connect() as conn:
        conn.execute(text(
            'CREATE TABLE User (Username VARCHAR(50) PRIMARY KEY, Name VARCHAR(100), Gender VARCHAR(10), Location VARCHAR(100), Bio TEXT, Password VARCHAR(25), Email VARCHAR(50), joined DATETIME DEFAULT CURRENT_TIMESTAMP)'))
        conn.execute(text(
            'CREATE TABLE Posts (Post_ID INT PRIMARY KEY AUTO_INCREMENT, Posted_At DATETIME, Text TEXT, Image VARCHAR(255), Author_Username VARCHAR(50), FOREIGN KEY (Author_Username) REFERENCES User(Username) on delete cascade)'))
        conn.execute(text(
            'CREATE TABLE Comments (Comment_ID INT PRIMARY KEY AUTO_INCREMENT, Posted_At DATETIME, Text TEXT, Comment_On INT, commenter VARCHAR(50), FOREIGN KEY (Comment_On) REFERENCES Posts(Post_ID) on delete cascade, foreign key (commenter) REFERENCES User(Username) ON DELETE cascade)'))
        conn.execute(text(
            'CREATE TABLE Reactions_on_Posts (Post_ID INT, Username_of_Reactor VARCHAR(50), Reaction VARCHAR(50), PRIMARY KEY (Post_ID, Username_of_Reactor), FOREIGN KEY (Post_ID) REFERENCES Posts(Post_ID) on delete cascade , FOREIGN KEY (Username_of_Reactor) REFERENCES User(Username) on delete cascade)'))
        conn.execute(text(
            "CREATE TABLE Friendship (User1 VARCHAR(50), User2 VARCHAR(50), Since DATETIME, PRIMARY KEY (User1, User2), FOREIGN KEY (User1) REFERENCES User(Username) on delete cascade , FOREIGN KEY (User2) REFERENCES User(Username) on delete cascade)"))
        conn.commit()
        conn.execute(text(
            "CREATE TABLE pending_requests (sender VARCHAR(50), receiver VARCHAR(50), request_time DATETIME DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (sender, receiver), FOREIGN KEY (sender) REFERENCES user(Username) ON DELETE CASCADE, FOREIGN KEY (receiver) REFERENCES user(Username) ON DELETE CASCADE)"
        ))
        conn.commit()



initialize_database()
