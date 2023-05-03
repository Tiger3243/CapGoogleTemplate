from app import app
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Sleep
from app.classes.forms import SleepForm
from flask_login import login_required
import datetime as dt

#This route actually does two things depending on the state of the if statement 
# 'if form.validate_on_submit()'. When the route is first called, the form has not 
# been submitted yet so the if statement is False and the route renders the form.
# If the user has filled out and succesfully submited the form then the if statement
# is True and this route creates the new blog based on what the user put in the form.
# Because this route includes a form that both gets and blogs data it needs the 'methods'
# in the route decorator.
@app.route('/sleep/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def sleepNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = SleepForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new blog form. 
        # Blog() is a mongoengine method for creating a new blog. 'newBlog' is the variable 
        # that stores the object that is the result of the Blog() method.  
        newSleep = Sleep(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            rating = form.rating.data,
            note = form.note.data,
            author = current_user.id,
            # This sets the modifydate to the current datetime.
            modify_date = dt.datetime.utcnow
        )
        # This is a method that saves the data to the mongoDB database.
        newSleep.save()

        # Once the new blog is saved, this sends the user to that blog using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a blog so we want 
        # to send them to that blog. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('sleep',sleepID=newSleep.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at blogform.html to 
    # see how that works.
    return render_template('sleepform.html',form=form)


@app.route('/sleep/<sleepID>')
@login_required
def sleep(sleepID):
    # retrieve the blog using the blogID
    thisSleep = Sleep.objects.get(id=sleepID)
    # If there are no comments the 'comments' object will have the value 'None'. Comments are 
    # related to blogs meaning that every comment contains a reference to a blog. In this case
    # there is a field on the comment collection called 'blog' that is a reference the Blog
    # document it is related to.  You can use the blogID to get the blog and then you can use
    # the blog object (thisBlog in this case) to get all the comments.
    # Send the blog object and the comments object to the 'blog.html' template.
    return render_template('sleep.html',sleep=thisSleep)

@app.route('/sleep/list')
@app.route('/sleeps')
@login_required
def sleepList():
    # This retrieves all of the 'blogs' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'blogs'.
    sleeps= Sleep.objects()
    # This renders (shows to the user) the blogs.html template. it also sends the blogs object 
    # to the template as a variable named blogs.  The template uses a for loop to display
    # each blog.
    return render_template('sleeps.html',sleeps=sleeps)

@app.route('/sleep/edit/<sleepID>', methods=['GET', 'POST'])
@login_required
def sleepEdit(sleepID):
    editSleep = Sleep.objects.get(id=sleepID)
    # if the user that requested to edit this blog is not the author then deny them and
    # send them back to the blog. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editSleep.author:
        flash("You can't edit a entry you don't own.")
        return redirect(url_for('sleepform',sleepID=sleepID))
    # get the form object
    form = SleepForm()
    # If the user has submitted the form then update the blog.
    if form.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editSleep.update(
            rating = form.rating.data,
            note = form.note.data,
            modify_date = dt.datetime.utcnow
        )
        # After updating the document, send the user to the updated blog using a redirect.
        return redirect(url_for('sleep',sleepID=sleepID))

    # if the form has NOT been submitted then take the data from the editBlog object
    # and place it in the form object so it will be displayed to the user on the template.
    form.rating.data = editSleep.rating
    form.note.data = editSleep.note

    # Send the user to the blog form that is now filled out with the current information
    # from the form.
    return render_template('sleepform.html',form=form)