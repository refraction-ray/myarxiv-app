"""
error handler function for exceptions
"""
from flask import render_template, jsonify
from .exceptions import *


def on_404(e):
    return render_template('404.html'), 404


def on_500(e):
    return jsonify({"message": "internal error"}), 500


def on_InvalidInput(e):
    response = jsonify(e.to_dict())
    response.status_code = e.status_code
    return response


def on_PermissionDenied(e):
    response = jsonify(e.to_dict())
    response.status_code = e.status_code
    return response
