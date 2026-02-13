from flask import Flask, render_template, request, redirect
import function 

app = Flask(__name__)

@app.route('/')
def index():
    total, remaining = function.get_summary()
    history = function.load_data()  
    return render_template('index.html', total=total, remaining=remaining, history=reversed(history))

@app.route('/add', methods=['POST'])
def add_expense():
    date = request.form.get('date')
    amount = request.form.get('amount')
    category = request.form.get('category')
    
    function.save_expense(date, amount, category)
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
    