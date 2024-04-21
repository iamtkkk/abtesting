from . import labAPI
from flask import jsonify, render_template, request, session, redirect, url_for
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

@labAPI.route('/testapi', methods=['GET'])
def api_entry():
    collection_names = db.list_collection_names()
    response = {
        'data': "API Running",
        'collection_names': collection_names
    }
    return jsonify(response)


def is_logged_in():
    return 'user_id' in session

@labAPI.route('/login', methods=['GET', 'POST'])
def login_admin_lab():
    if request.method == 'POST':
        data = request.form.to_dict()
        user = db.users.find_one({'email': data['email']})
        if user and user['password'] == data['password']:
            session['user_id'] = str(user['_id'])
            session['admin'] = True
            return redirect(url_for('labAPI.dashboard'))
        else:
            error = 'Invalid email or password'
            return render_template('lab/login.html', title='Login', error=error)
    else:
        if is_logged_in():
            return redirect(url_for('labAPI.dashboard'))
        return render_template('lab/login.html', title='Login', error='')
    
@labAPI.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('labAPI.login_admin_lab'))



    
@labAPI.route('/reach', methods=['GET'])
def reach():
    if is_logged_in() and session['admin']:

        visitors_count_A = db.visitors.count_documents({'page': 'A'})
        visitors_click_A = db.click_actions.count_documents({'page': 'A'})
        visitors_count_B = db.visitors.count_documents({'page': 'B'})
        visitors_click_B = db.click_actions.count_documents({'page': 'B'})
        
        save_A = db.click_actions.count_documents({'page': 'A', 'button': 'save'})
        save_B = db.click_actions.count_documents({'page': 'B', 'button': 'save'})
        login_A = db.click_actions.count_documents({'page': 'A', 'button': 'login'})
        login_B = db.click_actions.count_documents({'page': 'B', 'button': 'login'})
        register_A = db.click_actions.count_documents({'page': 'A', 'button': 'register'})
        register_B = db.click_actions.count_documents({'page': 'B', 'button': 'register'})
        viewmore_A = db.click_actions.count_documents({'page': 'A', 'button': 'viewmore'})
        viewmore_B = db.click_actions.count_documents({'page': 'B', 'button': 'viewmore'})


        data = {
            'visitors_count': {
                'A': visitors_count_A,
                'B': visitors_count_B
            },
            'visitors_click': {
                'A': visitors_click_A,
                'B': visitors_click_B
            },
            'save': {
                'A': save_A,
                'B': save_B
                },
            'login': {
                'A': login_A,
                'B': login_B
                },
            'register': {
                'A': register_A,
                'B': register_B
                },
            'viewmore': {
                'A': viewmore_A,
                'B': viewmore_B
            }
        }
        return render_template('lab/reach.html', title='Reach', data=data)
    else:
        return redirect(url_for('labAPI.login_admin_lab'))
    
# Calucator ---------------------
@labAPI.route('/calculator')
def calculator():
    if is_logged_in() and session['admin']:

        # get args from url
        button = (request.args.get('button') or "save")
        visitors_A = int(request.args.get('visitors_a') or 999999)
        visitors_B = int(request.args.get('visitors_b') or 999999)
        conversion_A = int(request.args.get('conversions_a') or 99999)
        conversion_B = int(request.args.get('conversions_b') or 99999)
        
        conversion_rate_A = conversion_A / visitors_A * 100
        conversion_rate_B = conversion_B / visitors_B * 100

        # data from db
        visitors_count_A = db.visitors.count_documents({'page': 'A'})
        visitors_count_B = db.visitors.count_documents({'page': 'B'})

        visitors_click_A = db.click_actions.count_documents({'page': 'A'})
        visitors_click_B = db.click_actions.count_documents({'page': 'B'})
        
        visitors_click_A_save = db.click_actions.count_documents({'page': 'A', 'button': button})
        visitors_click_B_save = db.click_actions.count_documents({'page': 'B', 'button': button})
        
        if (button == "all"):
            visitors_click_A_save = db.click_actions.count_documents({'page': 'A'})
            visitors_click_B_save = db.click_actions.count_documents({'page': 'B'})
        
                




        alpha = float(request.args.get('significance_level') or 0.05) 
        two_tails = request.args.get('method') or 'two'

        # Change twotails to bool
        if two_tails == 'two':
            two_tails = True
            alpha = alpha * 2
        else:
            two_tails = False
        print(visitors_A, visitors_B, conversion_A, conversion_B, alpha,two_tails )

        # Calculate
        test = Frequentist(visitors_A, conversion_A, visitors_B, conversion_B, alpha=alpha, two_tails=two_tails)
        test.get_z_value()

        # Print all the attributes
        print("Test Visitor A", test.visitors_A)
        print("Test Visitor B", test.visitors_B)
        print("Test Conversion A", test.conversions_A)
        print("Test Conversion B", test.conversions_B)
        print("Test Alpha", test.alpha)
        print("Test Two Tails", test.two_tails)
        print("Test Control CR", test.control_cr)
        print("Test Variant CR", test.variant_cr)
        print("Test Relative Difference", test.relative_difference)
        print("Test Control SE", test.control_se)
        print("Test Variant SE", test.variant_se)
        print("Test SE Difference", test.se_difference)
    
        z_score, p_value = test.z_test()
        print("Z Score", z_score)
        print("P Value", p_value)

        power = test.get_power()
        print("Power", round(power/100))

        # Calculate uplift
        uplift_a = round(((conversion_A / visitors_A * 100) * 100) / (conversion_B / visitors_B * 100)-100, 4) 
        uplift_b = round(((conversion_B / visitors_B * 100) * 100) / (conversion_A / visitors_A * 100)-100, 4) 

        isAmB = (uplift_a > uplift_b)
        isSignificant = p_value < alpha
        print(isAmB, uplift_a, uplift_b, isSignificant)

        xper = 0
        if isAmB :
            xper = ((conversion_rate_B - conversion_rate_A) / conversion_rate_B) * 100
        else:
            xper = ((conversion_rate_A - conversion_rate_B) / conversion_rate_A) * 100

            
        xper = abs(xper)
        
        #fig_test = test.plot_test_visualisation()
        #fig_power = test.plot_power()

        # Convert the test figure to a bytes-like object
        
        #buf_test = BytesIO()
        #fig_test.savefig(buf_test, format='png')
        #buf_test.seek(0)

        # Encode the bytes-like object of the test figure as a base64 string
        
        #fig_test_base64 = base64.b64encode(buf_test.read()).decode('utf-8')

        # Close the test figure to release memory
        
       # plt.close(fig_test)

        # Convert the power figure to a bytes-like object
        
       # buf_power = BytesIO()
        #fig_power.savefig(buf_power, format='png')
       # buf_power.seek(0)

        # Encode the bytes-like object of the power figure as a base64 string
        #fig_power_base64 = base64.b64encode(buf_power.read()).decode('utf-8')

        # Close the power figure to release memory
        #plt.close(fig_power)
        
        bar_chart_labels = ["A Best" if isAmB  else "A", "B Best" if not isAmB  else "B"]
        bar_chart_data_A = [ conversion_rate_A, conversion_rate_B]
        bar_chart_data_B = [ conversion_rate_B, conversion_rate_A]

        data = {
            'visitors_count': {
                'A': visitors_count_A,
                'B': visitors_count_B
            },
            'visitors_click': {
                'A': visitors_click_A,
                'B': visitors_click_B,
                'A_save': visitors_click_A_save,
                'B_save': visitors_click_B_save
            },
            'bar_chart': {
                'labels': bar_chart_labels,
                'dataA': bar_chart_data_A,
                'dataB': bar_chart_data_B
            },
            'Abest' : "A Best" if isAmB  else "A",
            'Bbest' : "B Best" if not isAmB  else "B",
        }
        


        # Pass the base64 strings to the template
        #return render_template('lab/calculator.html', title='Calculator', fig_test=fig_test_base64, fig_power=fig_power_base64,
        #                       test=test, z_score=z_score, p_value=p_value, power=power, uplift_a=uplift_a, uplift_b=uplift_b, isAmB=isAmB, isSignificant=isSignificant,
          #                     data=data)
        return render_template('lab/calculator.html', title='Calculator', 
                               test=test, z_score=z_score, xper=xper, p_value=p_value, power=power, uplift_a=uplift_a, uplift_b=uplift_b, isAmB=isAmB, isSignificant=isSignificant,
                               data=data)
    else:
        return redirect(url_for('labAPI.login_admin_lab'))

def calculate_frequentist(visitors_A, visitors_B, conversion_A, conversion_B, alpha, two_tails):
    test = Frequentist(visitors_A, conversion_A, visitors_B, conversion_B, alpha=alpha, two_tails=two_tails)

    return  test

