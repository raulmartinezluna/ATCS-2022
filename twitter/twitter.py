from models import *
from database import init_db, db_session
from datetime import datetime

class Twitter:

    currentUser = None

    """
    The menu to print once a user has logged in
    """
    def print_menu(self):
        print("\nPlease select a menu option:")
        print("1. View Feed")
        print("2. View My Tweets")
        print("3. Search by Tag")
        print("4. Search by User")
        print("5. Tweet")
        print("6. Follow")
        print("7. Unfollow")
        print("0. Logout")
    
    """
    Prints the provided list of tweets.
    """
    def print_tweets(self, tweets):
        for tweet in tweets:
            print("==============================")
            print(tweet)
        print("==============================")

    """
    Should be run at the end of the program
    """
    def end(self):
        print("Thanks for visiting!")
        db_session.remove()
    
    """
    Registers a new user. The user
    is guaranteed to be logged in after this function.
    """
    def register_user(self):
        #Loops until it gets valid values
        while True:
            username = input("What will your twitter handle be?\n")
            password = input("Enter a password:\n")

            if password == input("Re-enter your password:\n"):
                user = db_session.query(User).where(User.username == username).first()
                if user is None:
                    db_session.add(User(username, password))
                    db_session.commit()
                    self.currentUser = user
                    break
                else:
                    print("The username is already taken. Try again.")
            else:
                print("The passwords don't match. Try again.")
            print("\n\n")

    """
    Logs the user in. The user
    is guaranteed to be logged in after this function.
    """
    def login(self):
        #Loops until it gets valid values
        while True:
            username = input("Username: ")
            password = input("Password: ")

            user = db_session.query(User).where((User.username == username) & (User.password == password)).first()

            if user is not None:
                self.currentUser = user
                print(self.currentUser)
                break
            else:
                print("Invalid username or password")
    
    def logout(self):
        self.currentUser = None

    """
    Allows the user to login,  
    register, or exit.
    """
    def startup(self):
        #Loops until it gets valid values
        while True:
            print("Please select a Menu Option")
            selection = input("1. Login\n2. Register User\n0. Exit\nSelect: ")
            #By returning by an int we can use that as a code to determine if we should end the program in the menu method which it returns to
            if selection == "1":
                self.login()
                return 1
            elif selection == "2":
                self.register_user()
                return 1
            elif selection == "0":
                return 0
            print("\nInvalid selection\n\n")

    def follow(self):
        while True:
            otherUsername = input("Who would you like to follow\n")
            otherUser = db_session.query(User).where(User.username == otherUsername).first()
            if otherUser is not None:
                followerInstance = db_session.query(Follower).where((Follower.follower_id == self.currentUser.username) & (Follower.following_id == otherUsername)).first()
                msg = ""
                if followerInstance is None:
                    newFollower = Follower(self.currentUser.username, otherUsername)
                    db_session.add(newFollower)
                    db_session.commit()
                    msg = "You are now following @"
                else:
                    msg = "You already follow @"
                msg += otherUsername
                print(msg)
                break
            else:
                print("User does not exist. Try again.")

    def unfollow(self):
        while True:
            otherUsername = input("Who would you like to unfollow\n")
            otherUser = db_session.query(User).where(User.username == otherUsername).first()
            if otherUser is not None:
                followerInstance = db_session.query(Follower).where((Follower.follower_id == self.currentUser.username) & (Follower.following_id == otherUsername)).first()
                msg = ""
                if followerInstance is not None:
                    db_session.delete(followerInstance)
                    db_session.commit()
                    msg = "You no longer follow @"
                else:
                    msg = "You don't follow @"
                msg += otherUsername
                print(msg)
                break
            else:
                print("User does not exist. Try again.")

    def tweet(self):
        #Asks the user for content and tags
        content = input("Create Tweet: ")
        tags = input("Enter your tags seperated by spaces: ")

        #Makes a list of the tags
        tags = tags.split()

        #Takes out the # from each element
        tags = [x.strip("#") for x in tags]

        #Adds Tweet to Database
        db_session.add(Tweet(content, datetime.now(), self.currentUser.username))
        db_session.flush()

        #Adds Tags to Database
        for tag in tags:
            tagInstance = db_session.query(Tag).where(Tag.content == tag).first()
            if tagInstance is None:
                db_session.add(Tag(tag))
        db_session.flush()

        #Links Tweet and Tags
        for tag in tags:
            tweetID = db_session.query(Tweet).where(Tweet.content == content).first()
            tagID = db_session.query(Tag).where(Tag.content == tag).first()
            db_session.add(TweetTag(tweetID.id, tagID.id))
        db_session.flush()
        
        #Save
        db_session.commit()
    
    def view_my_tweets(self):
        #Print tweets
        currentUserTweets = db_session.query(Tweet).where(Tweet.username == self.currentUser.username).all()
        self.print_tweets(currentUserTweets)
    
    """
    Prints the 5 most recent tweets of the 
    people the user follows
    """
    def view_feed(self):
        #Find tweets of people the current user follows.
        follows = db_session.query(Follower).where(Follower.follower_id == self.currentUser.username).all()
        followsUsernames = [x.following_id for x in follows]

        # Source for IN operator from SQL to SQLAlchemy python https://www.geeksforgeeks.org/how-to-use-the-in-operator-in-sqlalchemy-in-python/
        # Source for getting the most recent object by datetime https://stackoverflow.com/questions/20937866/sqlalchemy-get-the-object-with-the-most-recent-date
        tweets = db_session.query(Tweet).filter(Tweet.username.in_(followsUsernames)).order_by(Tweet.timestamp.desc()).limit(5).all()

        #Print Tweets
        self.print_tweets(tweets)

    def search_by_user(self):
        #Asks user who he wants to search for.
        searchUsername = input("Whose tweets would you like to view?\n")

        #Find user and print out their tweets.
        user = db_session.query(User).where(User.username == searchUsername).first()
        if user is not None:
            self.print_tweets(user.tweets)
        else:
            print("There is no user by that name")

    def search_by_tag(self):
        #Asks user what tag he wants to search for.
        tagContent = input("What hashtag would you like to view the tweets by?\n#")

        #Find tag and print out related tweets.
        tag = db_session.query(Tag).where(Tag.content == tagContent).first()
        if tag is not None:
            self.print_tweets([x.tweet for x in tag.tweettag])
        else:
            print("There are no tweets with this tag")

    """
    Allows the user to select from the 
    ATCS Twitter Menu
    """
    def run(self):
        init_db()

        print("Welcome to ATCS Twitter!")
        if self.startup() == 1:

            while True:
                self.print_menu()
                option = int(input(""))

                if option == 1:
                    self.view_feed()
                elif option == 2:
                    self.view_my_tweets()
                elif option == 3:
                    self.search_by_tag()
                elif option == 4:
                    self.search_by_user()
                elif option == 5:
                    self.tweet()
                elif option == 6:
                    self.follow()
                elif option == 7:
                    self.unfollow()
                else:
                    self.logout()
                    break
        self.end()