from flask import abort

def populate_comment(form, comment):
    comment.title = form.title.data
    comment.text = form.text.data
