from . import apiAPI
from flask import jsonify, render_template, request, session, redirect, url_for
from config.db import db
from datetime import datetime
import random
from datetime import timedelta

@apiAPI.route('/v1', methods=['GET'])
def api_entry():
    response = {
        'data': "API Running",
    }
    return jsonify(response)


@apiAPI.route('/save-click-action', methods=['POST'])
def save_click_action():
    data = request.json

    page = data.get('page')
    if not page:
        return jsonify({'error': 'Page parameter is missing'}), 400

    user_id = session.get('user_id') or 'anonymous'

    try:
        db.click_actions.insert_one({
            'date_click': datetime.now(),
            'user_id': user_id,
            'button': data.get('button'),
            'page': page
        })
        return jsonify({'success': 'Click action saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apiAPI.route('/testpage', methods=['GET'])
def testpage():
    return render_template('test.html')

# Define a function to generate a random datetime within a specified range
def random_datetime(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

@apiAPI.route('/generate-random-click-action', methods=['GET'])
def generate_random_click_action():
    mockup_data = {
        'A' : {
            'save' : 50,
            'register' : 88,
            'login' : 92,
            'viewmore': 90
        },
        'B' : {
            'save' : 86,
            'register' : 74,
            'login' : 124,
            'viewmore': 120
        }
    }
    
    start_date = datetime.now() - timedelta(days=30)  
    user_id = session.get('user_id') or 'anonymous'

    try:
        
        for i in mockup_data:
            for j in mockup_data[i]:
                print(i, j, mockup_data[i][j])

                for _ in range(mockup_data[i][j]):
                    random_date = random_datetime(start_date, datetime.now())
                    db.click_actions.insert_one({
                        'date_click': random_date,
                        'user_id': user_id,
                        'button': j,
                        'page': i
                    })



        return jsonify({'success': f'{787878} random click actions and visitor data saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apiAPI.route('/generate-random-visitor', methods=['GET'])
def generate_random_visitor():
    num_visitors = 1000 
    start_date = datetime.now() - timedelta(days=30)  

    try:
        for i in ['A', 'B']:
            for _ in range(num_visitors):
                random_date = random_datetime(start_date, datetime.now())
                db.visitors.insert_one({
                    'date_visit': random_date,
                    'page': i
                })

        return jsonify({'success': f'{num_visitors} random visitors data saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@apiAPI.route('/dell', methods=['GET'])
def delete_all():
    db.click_actions.delete_many({})
    db.visitors.delete_many({})
    return {
        'status': 'deleted'
    }

@apiAPI.route('/export_click_action_to_csv', methods=['GET'])
def export_click_action_to_csv():
    import csv
    import json
    from bson import json_util

    click_actions = db.click_actions.find({})
    click_actions = json.loads(json_util.dumps(click_actions))

    with open('click_actions.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['date_click', 'user_id', 'button', 'page'])
        for click_action in click_actions:
            # Remove newline characters if they exist in the fields
            date_click = str(click_action['date_click']).replace('\n', '')
            user_id = str(click_action['user_id']).replace('\n', '')
            button = str(click_action['button']).replace('\n', '')
            page = str(click_action['page']).replace('\n', '')
            writer.writerow([date_click, user_id, button, page])
    
    return {
        'status': 'exported'
    }
    
@apiAPI.route('/export_visitors_to_csv', methods=['GET'])
def export_visitors_to_csv():
    import csv
    import json
    from bson import json_util

    visitors = db.visitors.find({})
    visitors = json.loads(json_util.dumps(visitors))

    with open('visitors.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['date_visit', 'page'])
        for visitor in visitors:
            # Remove newline characters if they exist in the fields
            date_visit = str(visitor['date_visit']).replace('\n', '')
            page = str(visitor['page']).replace('\n', '')
            writer.writerow([date_visit, page])
    
    return {
        'status': 'exported'
    }

    