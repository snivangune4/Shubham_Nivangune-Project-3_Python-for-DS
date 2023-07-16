from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import pickle

app = Flask(__name__)
app.secret_key = '141299'
app.app_context().push()

# Load the saved model
model = pickle.load(open('loan_eligibility_model.pkl', 'rb'))

# Configure MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Coc#0611@localhost/Loan_Prediction_db'
db = SQLAlchemy(app)


# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# Create the users table in the database
db.create_all()


# Register API
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        user = User.query.filter_by(username=username).first()
        if user:
            return '''
                <h1>Username Already Exists!</h1>
                <button onclick="location.href='/register'">Register</button>
                <button onclick="location.href='/login'">Login</button>
                '''

        # Create a new user and add it to the database
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')


# Login API
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password are correct
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = user.username
            return redirect('/enter_details')
        else:
            return '''
                <h1>Invalid username or password! Please enter correct details</h1>
                <button onclick="location.href='/login'">Login</button>
                '''

    return render_template('login.html')


# Enter Details API
@app.route('/enter_details', methods=['GET', 'POST'])
def enter_details():
    # if 'user_id' not in session:
    #     return redirect('/login')

    if request.method == 'POST':
        # Retrieve the entered details from the form
        gender = request.form['gender']
        married = request.form['married']
        dependents = request.form['dependents']
        self_employed = request.form['self_employed']
        education = request.form['education']
        applicant_income = float(request.form['applicant_income'])
        coapplicant_income = float(request.form['coapplicant_income'])
        loan_amount = float(request.form['loan_amount'])
        loan_amount_term = float(request.form['loan_amount_term'])
        credit_history = float(request.form['credit_history'])
        property_area = request.form['property_area']

        # Prepare the input for prediction
        input_data = [[gender, married, dependents, education, self_employed, applicant_income,
                       coapplicant_income, loan_amount, loan_amount_term, credit_history, property_area]]

        # Make the prediction
        prediction = model.predict(input_data)
        if prediction > 0.5:
            prediction = "Congratulations! You are eligible for the loan"

        else:
            prediction = "Sorry, you are not eligible for the loan"

        return render_template('predict.html', prediction=prediction)

    return render_template('predict.html')


# Logout API
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


# Home API
@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
