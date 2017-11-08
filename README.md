# Blogz
## A simple blogging web app

Written in python using the Flask framework and Jinja2 for HTML templating, the Blogz app uses MySQL to manage the database of users and blog posts, using foreign keys to tie posts to their users.

Basic Navigation includes a Home page that lists all the blog users, a page for All Posts by all users, and a New Post page, which is only accessible after logging in.
[[https://github.com/ajwallacemusic/blogz/blob/master/Blogz%20-%20Main%20Navigation_480p.gif]]
Logging in allows users to create new posts

Signing up allows users to create an account with a secure sha-256 encrytpted and salted password.
