from flask import Flask, render_template, request, redirect, session
from config import Config
from models import User, Repair, Assignment, MaintenanceRecord, Payment, Evaluation, db
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.route('/')
def index():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        userpassword = request.form['userpassword']

        user = User.query.filter_by(username=username, userpassword=userpassword).first()

        if user:
            session['userid'] = user.userid
            session['role'] = user.role

            if user.role == 'owner':
                return redirect('/owner')
            elif user.role == 'service':
                return redirect('/service')
            elif user.role == 'worker':
                return redirect('/worker')
            elif user.role == 'finance':
                return redirect('/finance')
        else:
            return "用户名或密码错误"

    return render_template('login.html')


@app.route('/owner')
def owner_dashboard():
    if 'userid' not in session or session.get('role') != 'owner':
        return redirect('/login')

    repairs = Repair.query.filter_by(owner_id=session['userid'])\
                .order_by(Repair.created_at.desc()).all()

    evaluations = Evaluation.query.all()

    return render_template(
        'owner_dashboard.html',
        repairs=repairs,
        evaluations=evaluations
    )

@app.route('/service', methods=['GET', 'POST'])
def service_page():
    if request.method == 'POST':
        repair_id = request.form['repair_id']
        worker_id = request.form['worker_id']

        new_assignment = Assignment(
            repair_id=repair_id,
            worker_id=worker_id
        )

        db.session.add(new_assignment)

        repair = Repair.query.get(repair_id)
        repair.status = 'assigned'

        db.session.commit()

        #return "派工成功"
        return redirect('/service')

    pending_repairs = Repair.query.filter_by(status='pending').all()
    workers = User.query.filter_by(role='worker').all()

    return render_template(
        'service_dashboard.html',
        repairs=pending_repairs,
        workers=workers
    )


@app.route('/worker', methods=['GET', 'POST'])
def worker_page():
    if request.method == 'POST':
        repair_id = request.form['repair_id']
        result = request.form['result']
        cost = request.form['cost']

        record = MaintenanceRecord(
            repair_id=repair_id,
            worker_id=session['userid'],
            result=result,
            cost=cost
        )

        payment = Payment(
            repair_id=repair_id,
            amount=cost,
            status='unpaid'
        )

        repair = Repair.query.get(repair_id)
        repair.status = 'completed'

        db.session.add(record)
        db.session.add(payment)
        db.session.commit()

        #return "维修记录提交成功"
        return redirect('/worker')

    assignments = Assignment.query.filter_by(worker_id=session['userid']).all()

    repairs = []
    for a in assignments:
        repair = Repair.query.get(a.repair_id)
        if repair.status == 'assigned':
            repairs.append(repair)

    return render_template('worker_dashboard.html', repairs=repairs)


@app.route('/finance', methods=['GET', 'POST'])
def finance_page():
    if request.method == 'POST':
        payment_id = request.form['payment_id']

        payment = Payment.query.get(payment_id)
        payment.status = 'paid'
        payment.paid_at = datetime.now()

        repair = Repair.query.get(payment.repair_id)
        repair.status = 'paid'

        db.session.commit()

        #return "收费完成"
        return redirect('/finance')

    unpaid_payments = Payment.query.filter_by(status='unpaid').all()

    return render_template('finance_dashboard.html', payments=unpaid_payments)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/submit_evaluation/<int:repair_id>', methods=['POST'])
def submit_evaluation(repair_id):
    if 'userid' not in session or session.get('role') != 'owner':
        return redirect('/login')

    # 检查是否已经评价过
    existing = Evaluation.query.filter_by(repair_id=repair_id).first()
    if existing:
        return redirect('/owner')

    rating = request.form['rating']
    comment = request.form['comment']

    evaluation = Evaluation(
        repair_id=repair_id,
        rating=rating,
        comment=comment
    )

    db.session.add(evaluation)
    db.session.commit()

    return redirect('/owner')

@app.route('/submit_repair', methods=['POST'])
def submit_repair():
    if 'userid' not in session or session.get('role') != 'owner':
        return redirect('/login')

    repair_type = request.form['repair_type']
    description = request.form['description']

    new_repair = Repair(
        owner_id=session['userid'],
        repair_type=repair_type,
        description=description,
        status='pending'
    )

    db.session.add(new_repair)
    db.session.commit()

    return redirect('/owner')

if __name__ == '__main__':
    app.run(debug=True)
