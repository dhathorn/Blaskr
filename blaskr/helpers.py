from flask import abort

def populate_titletext(form, comment):
    comment.title = form.title.data
    comment.text = form.text.data
