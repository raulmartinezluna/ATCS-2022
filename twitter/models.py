"""
The file that holds the schema/classes
that will be used to create objects
and connect to data tables.
"""

from sqlalchemy import ForeignKey, Column, INTEGER, TEXT, DATETIME
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    # Columns
    username = Column("username", TEXT, primary_key=True)
    password = Column("password", TEXT, nullable=False)

    #Relationships
    following = relationship("User", 
                             secondary="followers",
                             primaryjoin="User.username==Follower.follower_id",
                             secondaryjoin="User.username==Follower.following_id")
    
    followers = relationship("User", 
                             secondary="followers",
                             primaryjoin="User.username==Follower.following_id",
                             secondaryjoin="User.username==Follower.follower_id",
                             overlaps="following")
    tweets = relationship("Tweet", back_populates="user")

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return "@" + self.username

class Follower(Base):
    __tablename__ = "followers"

    # Columns
    id = Column("id", INTEGER, primary_key=True)
    follower_id = Column('follower_id', TEXT, ForeignKey("users.username"))
    following_id = Column('following_id', TEXT, ForeignKey("users.username"))

    def __init__(self, follower_id, following_id):
        self.follower_id = follower_id
        self.following_id = following_id

class Tweet(Base):
    # TODO: Complete the class

    __tablename__ = "tweets"

    #Columns
    id = Column("id", INTEGER, primary_key=True)
    content = Column("content", TEXT, nullable=False)
    timestamp = Column("timestamp", DATETIME, nullable=False)
    username = Column("username", TEXT, ForeignKey("users.username"))

    #Relationships
    user = relationship("User", back_populates="tweets")
    tweettag = relationship("TweetTag", back_populates="tweet")
    
    def __init__(self, content, timestamp, username):
        self.content = content
        self.timestamp = timestamp
        self.username = username

    def __repr__(self):
        name = self.user.username
        tweetText = self.content
        tags = "".join(["#"+x.tag.content+" " for x in self.tweettag])
        time = self.timestamp
        return "@{}:\n{}\n{}\n{}".format(name, tweetText, tags, time)

class Tag(Base):
    # TODO: Complete the class

    __tablename__ = "tags"

    #Columns
    id = Column("id", INTEGER, primary_key=True)
    content = Column("content", TEXT, nullable=False)

    #Relationships
    tweettag = relationship("TweetTag", back_populates="tag")

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return "#" + self.content

class TweetTag(Base):
    # TODO: Complete the class

    __tablename__ = "tweettags"
    
    #Columns
    id = Column("id", INTEGER, primary_key=True)
    tweet_id = Column("tweet_id", TEXT, ForeignKey("tweets.id"))
    tag_id = Column("tag_id", TEXT, ForeignKey("tags.id"))

    #Relationships
    tweet = relationship("Tweet", back_populates="tweettag")
    tag = relationship("Tag", back_populates="tweettag")

    def __init__(self, tweet_id, tag_id):
        self.tweet_id = tweet_id
        self.tag_id = tag_id