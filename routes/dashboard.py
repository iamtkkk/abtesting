from . import labAPI
from flask import jsonify, render_template, request, session, redirect, url_for, send_file
from config.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
from .frequentist import Frequentist
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as scs
import matplotlib.ticker as mtick
import seaborn as sns
from io import BytesIO
import base64
import random
import calendar
import plotly.graph_objects as go
import os
import base64


from datetime import datetime, timedelta

def is_logged_in():
    return 'user_id' in session

def calculate_frequentist(visitors_A, visitors_B, conversion_A, conversion_B, alpha, two_tails):
    test = Frequentist(visitors_A, conversion_A, visitors_B, conversion_B, alpha=alpha, two_tails=two_tails)
    return  test

@labAPI.route('/dashboard')
def dashboard():
    if is_logged_in() and session['admin']:
        page = request.args.get('page') or 'all'
        button = request.args.get('button') or 'save'
        time_frame = request.args.get('time_frame') or 'seven'

        visitors_count_A = db.visitors.count_documents({'page': 'A'})
        visitors_count_B = db.visitors.count_documents({'page': 'B'})

        visitors_click_A = db.click_actions.count_documents({'page': 'A'})
        visitors_click_save_A = db.click_actions.count_documents({'page': 'A', 'button': 'save'})
        visitors_click_register_A = db.click_actions.count_documents({'page': 'A', 'button': 'register'})
        

        visitors_click_B = db.click_actions.count_documents({'page': 'B'})
        visitors_click_save_B = db.click_actions.count_documents({'page': 'B', 'button': 'save'})
        visitors_click_register_B = db.click_actions.count_documents({'page': 'B', 'button': 'register'})
        
        save_A = db.click_actions.count_documents({'page': 'A', 'button': 'save'})
        save_B = db.click_actions.count_documents({'page': 'B', 'button': 'save'})
        login_A = db.click_actions.count_documents({'page': 'A', 'button': 'login'})
        login_B = db.click_actions.count_documents({'page': 'B', 'button': 'login'})
        register_A = db.click_actions.count_documents({'page': 'A', 'button': 'register'})
        register_B = db.click_actions.count_documents({'page': 'B', 'button': 'register'})
        viewmore_A = db.click_actions.count_documents({'page': 'A', 'button': 'viewmore'})
        viewmore_B = db.click_actions.count_documents({'page': 'B', 'button': 'viewmore'})

        
        
        
        line_label = []
        if time_frame == 'month':
            today = datetime.now()
            line_label = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
        elif time_frame == 'half':
            today = datetime.now()
            line_label = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(15)]
        elif time_frame == 'seven':
            today = datetime.now()
            line_label = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        else:
            today = datetime.now()
            line_label = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
        line_chart_data_A = []
        line_chart_data_B = []

        line_label = sorted(line_label, reverse=False)
        for date_str in line_label:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            date_midnight = datetime.combine(date, datetime.min.time())
            clicks_A = db.click_actions.count_documents({'page': 'A', 'date_click': {"$gte": date_midnight, "$lt": date_midnight + timedelta(days=1)}})
            line_chart_data_A.append(clicks_A)
            clicks_B = db.click_actions.count_documents({'page': 'B', 'date_click': {"$gte": date_midnight, "$lt": date_midnight + timedelta(days=1)}})
            line_chart_data_B.append(clicks_B)


        bar_chart_labels = ['Buy', 'Register', 'Login', 'View More']
        bar_chart_data_A = [save_A, register_A, login_A, viewmore_A]
        bar_chart_data_B = [save_B, register_B, login_B, viewmore_B]

        # Check page
        if page == 'all':
            visitors_count_display = visitors_count_A + visitors_count_B
        else:
            visitors_count_display = db.visitors.count_documents({'page': page})
        
        # Chekc click
        click_count_A = visitors_click_A
        click_count_B = visitors_click_B
        
        #check button
        if button == 'all':
            pass 
        elif button == 'save':
            bar_chart_labels = ['Buy']
            bar_chart_data_A = [save_A]
            bar_chart_data_B = [save_B]  
            click_count_A = visitors_click_save_A
            click_count_B = visitors_click_save_B   
            
        elif button == 'register':
            bar_chart_labels = ['Register']
            bar_chart_data_A = [register_A]
            bar_chart_data_B = [register_B]
            click_count_A = visitors_click_register_A
            click_count_B = visitors_click_register_B
            
        elif button == 'login':
            bar_chart_labels = ['Login']
            bar_chart_data_A = [login_A]
            bar_chart_data_B = [login_B]
            click_count_A = login_A
            click_count_B = login_B
            
        elif button == 'viewmore':
            bar_chart_labels = ['View More']
            bar_chart_data_A = [viewmore_A]
            bar_chart_data_B = [viewmore_B]
            click_count_A = viewmore_A
            click_count_B = viewmore_B
                

        test = calculate_frequentist(visitors_count_A, visitors_count_B, click_count_A, click_count_B, 0.05, True)

        test.get_z_value()
        z_score, p_value = test.z_test()
        power = test.get_power()

        z_score, p_value = test.z_test()
        
        

        isSignificant = p_value < 0.05*2


        data = {
            'page': page,
            'bg_color': "#5EC57E" if isSignificant else "#E4A11C",
            'visitors_click_A': click_count_A,
            'visitors_click_B': click_count_B,
            'convertion_rate_A': click_count_A / (visitors_count_A ) * 100,
            'convertion_rate_B': click_count_B / (visitors_count_B ) * 100,
            'button': button,
            'visitors_count_display': visitors_count_display,
            'frequentist': {
                'z_score': z_score,
                'p_value': p_value,
                'power': power,
                'test' : test,
            },
            'visitors_count': {
                'A': visitors_count_A if page == 'all' or page == 'A' else 0,
                'B': visitors_count_B if page == 'all' or page == 'B' else 0,
                'data': [visitors_count_A if page == 'all' or page == 'A' else 0, visitors_count_B if page == 'all' or page == 'B' else 0],
            },
            'bar_chart': {
                'labels': bar_chart_labels,
                'dataA': bar_chart_data_A if page == 'all' or page == 'A' else [],
                'dataB': bar_chart_data_B if page == 'all' or page == 'B' else [],
            },
            'line_chart': {
                'labels': line_label,
                'dataA': line_chart_data_A if page == 'all' or page == 'A' else [],
                'dataB': line_chart_data_B if page == 'all' or page == 'B' else []
            }
        }
        
        # Calculate uplift
        uplift_a = round(((click_count_A / visitors_count_A * 100) * 100) / (click_count_B / visitors_count_B * 100)-100, 4) 
        uplift_b = round(((click_count_B / visitors_count_B * 100) * 100) / (click_count_A / visitors_count_A * 100)-100, 4) 
        print(uplift_a, uplift_b, isSignificant)
        
        
        data['amoreb'] = uplift_a > uplift_b
        data['convertion_rate_A'] = "{:.2f}".format(data['convertion_rate_A'])
        data['convertion_rate_B'] = "{:.2f}".format(data['convertion_rate_B'])
        
        xper = 0
        if data['convertion_rate_A'] > data['convertion_rate_B']:
            xper = ((float(data['convertion_rate_A']) - float(data['convertion_rate_B'])) / float(data['convertion_rate_A'])) * 100
        else:
            xper =( (float(data['convertion_rate_B']) - float(data['convertion_rate_A'])) / float(data['convertion_rate_B'])) * 100
        
        if data['amoreb']:
            xper = (float(data['convertion_rate_B']) - float(data['convertion_rate_A'])) / (float(data['convertion_rate_B'])) * 100
        else:
            xper = (float(data['convertion_rate_A']) - float(data['convertion_rate_B'])) / (float(data['convertion_rate_A'])) * 100

        xper = abs(xper)

        #base64_image = save_plotly_graph_as_base64(visitors_click_A)

        #return render_template('lab/dashboard.html', title='Dashboard', data=data, isSignificant=isSignificant, plotly_image=base64_image)
        return render_template('lab/dashboard.html', title='Dashboard', data=data, isSignificant=isSignificant, xper=xper)
    else:
        return redirect(url_for('labAPI.login_admin_lab'))



def save_plotly_graph_as_base64(conversion_A):
    # Calculate the progress towards the target
    progress = min(conversion_A / 5000, 1.0)  # Limit progress to maximum of 1
    progress_percentage = min(conversion_A / 5000 * 100, 100)  # Limit progress to maximum of 100%
    progress_label = f"{conversion_A}/5000 ({progress_percentage:.2f}%)"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=progress,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Conversion A Progress"},
        gauge={
            'axis': {'range': [0, 1]},
            'steps': [
                {'range': [0, 0.5], 'color': "lightgray"},
                {'range': [0.5, 0.75], 'color': "lightgray"},
                {'range': [0.75, 1], 'color': "lightgray"}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': progress}}
    ))


    fig.add_annotation(
        text=progress_label,
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=20)
    )


    img_bytes = fig.to_image(format="png")
    base64_encoded_img = base64.b64encode(img_bytes).decode('utf-8')
    return base64_encoded_img
