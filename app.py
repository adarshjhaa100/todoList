from flask import Flask,request,render_template,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'
db = SQLAlchemy(app)


class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(200),nullable=False)
    password=db.Column(db.String(200),nullable=False)
    logged_in=db.Column(db.Boolean,default=False)
    def __repr__(self):
        return f'User({self.username})'

class Note(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    content=db.Column(db.String(500),nullable=False)
    date_created=db.Column(db.DateTime,default=datetime.now())
    date_modified=db.Column(db.DateTime,default=datetime.now())
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    user = db.relationship('User',
        backref=db.backref('notes', lazy=True)
        )
    def __repr__(self):
        return f'{self.user_id}-{self.id}'    


@app.route('/',methods=['GET','POST'])
def index():
    notes=Note.query.all()
    for i in notes:
        print(i.id,i.content)
    users=User.query.all()
    
    if request.method=='POST':
        credentials=request.form
        u=User.query.filter_by(username=credentials['username'],
        password=credentials['password']).first()
        
        if u is None:
            print('failed')
            return redirect('/')
        u.logged_in=True
        db.session.commit()
        return redirect(f'notes/{u.id}')
    return render_template('login.html')


@app.route('/notes/<int:u_id>',methods=['GET','POST'])
def view_notes(u_id):

    user=User.query.filter_by(id=u_id).first()
    if user==None or user.logged_in==False:
        return redirect('/')
    
    if request.method=='POST':
        content=request.form['content']
        n=Note(content=content,date_created=datetime.now(),date_modified=datetime.now())
        user.notes.append(n)
        db.session.commit()
        
    return render_template('notes.html',user=user,notes=user.notes)

@app.route('/delete/<int:uid>/<int:id>')
def delete(uid,id):
    note=Note.query.get_or_404(id)
    try:
        txt=note.content
        db.session.delete(note)
        db.session.commit()
        print(f'Deleted:{txt}')
        return redirect(f'/notes/{uid}')
    except:
        return 'Trouble deleting note'


@app.route('/update/<int:uid>/<int:id>',methods=['GET','POST'])
def modify(uid,id):
    user=User.query.filter_by(id=uid).first()
    note=Note.query.filter_by(id=id).first()
    
    mod=False
    if request.method=='POST':
        content=request.form['content']
        print(content)
        note.content=content
        note.date_modified=datetime.now()
        db.session.commit()
        return redirect(f'/notes/{uid}')
    return render_template('notes.html',user=user,notes=user.notes,note=note,modify=True)


@app.route('/logout/<int:id>')
def logout(id):
    user=User.query.filter_by(id=id).first()
    if user.logged_in:
        user.logged_in=False
        db.session.commit()
        return redirect('/')    
    return 'logout failed'
    
if(__name__=='__main__'):
    app.run(debug=True)