from flask import Flask, render_template, request, redirect, session
from config import Config
from models import db, User, Repair, Assignment, MaintenanceRecord, Payment
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


@app.route('/owner', methods=['GET', 'POST'])
def owner_page():
    if request.method == 'POST':
        repair_type = request.form['repair_type']
        description = request.form['description']

        try:
            new_repair = Repair(
                owner_id=session['userid'],
                repair_type=repair_type,
                description=description,
                status='pending'
            )

            db.session.add(new_repair)
            db.session.commit()

            return "报修提交成功"

        except Exception as e:
            db.session.rollback()
            return f"报错了: {str(e)}"

    return render_template('owner_dashboard.html')


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

        return "派工成功"

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

        return "维修记录提交成功"

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

        return "收费完成"

    unpaid_payments = Payment.query.filter_by(status='unpaid').all()

    return render_template('finance_dashboard.html', payments=unpaid_payments)


if __name__ == '__main__':
    app.run(debug=True)
