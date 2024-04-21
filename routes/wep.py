from . import defaultAPI
from flask import  jsonify, render_template, request, session, redirect, url_for, send_file, send_from_directory
import json
from .auth import is_logged_in, login_required
from config.db import db
from datetime import datetime

@defaultAPI.route('/')
def index():
    return render_template('index.html', title='Home A')


@defaultAPI.route('/A')
def indexA():
    page = 'A'
    user_id = session.get('user_id') or 'anonymous'

    try:
        db.visitors.insert_one({
            'date_visit': datetime.now(),
            'user_id': user_id,
            'page': page
        })
        return render_template('index.html', title='Home A')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@defaultAPI.route('/B')
def indexB():
    page = 'B'
    user_id = session.get('user_id') or 'anonymous'

    try:
        db.visitors.insert_one({
            'date_visit': datetime.now(),
            'user_id': user_id,
            'page': page
        })
        return render_template('indexB.html', title='Home B')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@defaultAPI.route('/img/<filename>')
def send_img(filename):
    return send_from_directory('./static/img', filename)

@defaultAPI.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))


@defaultAPI.route('/admin-panel')
def admin_panel():
    if session['admin']:
        return render_template('abtest/admin-panel.html', title='Admin Panel')
    else:
        return redirect(url_for('defaultAPI.index'))

# dynamic an specfy page
@defaultAPI.route('/admin-panel/<page>') 
def static_route(page):
    return render_template('abtest/'+page+'.html', title='Admin Panel')
    
