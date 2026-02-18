from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship


class Base(DeclarativeBase):
    pass


author_blogpost = Table(
    "author_blogpost",
    Base.metadata,
    Column("author_id", Integer, ForeignKey("author.id")),
    Column("blogpost_id", Integer, ForeignKey("blogpost.id")),
)


class Author(Base):
    __tablename__ = "author"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=False)

    blogposts = relationship(
        "BlogPost", back_populates="authors", secondary=author_blogpost
    )
    comments = relationship("Comment", back_populates="author")


class BlogPost(Base):
    __tablename__ = "blogpost"

    id = mapped_column(Integer, primary_key=True)
    published_at = mapped_column(DateTime, nullable=False)
    title = mapped_column(String, nullable=False)
    content = mapped_column(Text)

    authors = relationship(
        "Author", back_populates="blogposts", secondary=author_blogpost
    )
    comments = relationship("Comment", back_populates="blogpost")


class Comment(Base):
    __tablename__ = "comment"

    id = mapped_column(Integer, primary_key=True)
    content = mapped_column(Text)

    author_id = mapped_column(Integer, ForeignKey("author.id"))
    author = relationship("Author", back_populates="comments")
    blogpost_id = mapped_column(Integer, ForeignKey("blogpost.id"))
    blogpost = relationship("BlogPost", back_populates="comments")
