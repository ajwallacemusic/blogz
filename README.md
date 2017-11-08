# Blogz
## A simple blogging web app

Written in python using the Flask framework and Jinja2 for HTML templating, the Blogz app uses MySQL to manage the database of users and blog posts, using foreign keys to tie posts to their users.

Basic Navigation includes a Home page that lists all the blog users, a page for All Posts by all users, and a New Post page, which is only accessible after logging in.

![Blogz navigation gif](https://user-images.githubusercontent.com/24554274/32528213-74a7b430-c3f7-11e7-9d44-b7aa07a2e088.gif)


Logging in allows users to create new posts

Signing up allows users to create an account with a secure sha-256 encrytpted and salted password.
