from flask import (Flask, g, render_template, flash, redirect,
                    url_for, abort)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager,login_user,logout_user,
                    login_required,current_user)

# import crawler
import models
import forms
from price import price_grab,px_return,price
from live_post import get_new_posts, teaser

DEBUG = True
PORT = 5000
HOST = '127.0.0.1'

app = Flask(__name__)
app.secret_key = 'aldkfjaou2309u23rjJ!)#(U)@!R'

login_manager = LoginManager()
login_manager.init_app(app)
'''If they are on a page and need to login, redirect them
to the login view'''
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    '''Conenct to the Database before each request'''
    g.db = models.DATABASE
    g.user = current_user
    g.db.connect()

@app.after_request
def after_request(response):
    '''Close the Database connection after each request'''
    g.db.close()
    return response

@app.route('/register/user/',methods=('GET','POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("You have successfully registered", "success")
        models.User.create_user(
            username = form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html',form=form)

@app.route('/login',methods=('GET','POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password does not match!","error")
        else:
            if check_password_hash(user.password,form.password.data):
                login_user(user)
                flash("You've been logged in!","success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password does not match!","error")
    return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!','success')
    return redirect(url_for('index'))

@app.route('/new_post')
@login_required
def post():
    stream = models.Post.select().limit(100)
    writer_list = []
    for writer in models.Writer.select():
        writer_list.append(writer.name)
    title_list = teaser()
    a = get_new_posts(writer_list)
    for key,value in a.items():
        name,date,ticker,link,title,paragraph = value
        w_id = models.Writer.select().where(models.Writer.name==name).get().id
        try:
            true_symbol = price_grab(ticker,title,paragraph)
            symbol = true_symbol.name_dict['ticker']
            cost = true_symbol.name_dict['cost']
            exchange = true_symbol.name_dict['exchange']
            models.Post.create(link=link,symbol=symbol,exchange=exchange,
                title=title,entry_px=cost,entry=paragraph,writer_id=w_id)
        except:
            print('skipped')
    return render_template('stream.html',stream=stream,price=price,
    px_return=px_return)


@app.route('/')
@login_required
def index():
    stream = models.Post.select().limit(20)
    return render_template('stream.html',user=current_user,
    stream=stream,price=price,px_return=px_return)


@app.route('/stream')
@app.route('/stream/<int:userid>')
@login_required
def stream(userid=None):
    user = current_user
    if userid is None:
        template = 'stream.html'
        stream = models.Post.select().limit(20)
        return render_template(template,stream=stream,
        user=current_user,price=price,px_return=px_return)
    elif userid:
        template = 'user_stream.html'
        try:
            stream = models.Post.select(
            ).where(models.Post.writer_id == userid
            ).order_by(models.Post.timestamp).limit(20)
            writer = models.Writer.select(
            ).where(models.Writer.id == userid).get()
        except models.DoesNotExist:
            abort(404)
        else:
            return render_template(template,userid=userid,user=current_user,
            stream=stream,price=price,px_return=px_return,writer=writer)


@app.route('/view_stocks/<symbol>')
@login_required
def ticker(symbol=None):
    template = 'symbol.html'
    user = current_user
    stream = models.Post.select().where(models.Post.symbol == symbol
        ).limit(100)
    return render_template(template,stream=stream,user=user,
        price=price,symbol=symbol,px_return=px_return)


@app.route('/myadvisors/<int:viewid>')
@login_required
def myadvisors(viewid=None):
    if viewid:
        template = 'myadvisors.html'
        user = current_user
        stream = models.Post.select(models.Post,models.Writer
            ).join(models.Writer).join(models.Relationship,
            on=models.Relationship.to_user
            ).where(models.Relationship.from_user==viewid)
        return render_template(template,stream=stream,
        user=user,price=price,px_return=px_return)
    else:
        template = 'stream.html'
        stream = models.Post.select().limit(20)
        return render_template(template,stream=stream,user=current_user,
            price=price,px_return=px_return)

@login_required
@app.route('/addform',methods=('GET','POST'))
def add_form():
    form = forms.AddWriter()
    if form.validate_on_submit():
        user = current_user
        if user.is_admin:
            models.Writer.create(
                name=form.name.data.strip(),
                company=form.company.data.strip(),
                bio=form.bio.data.strip(),
                website=form.website.data.strip()
            )
            flash("Message Posted",'success')
            return redirect(url_for('index'))
        else:
            models.PropsectiveWriter.create(
                name=form.name.data.strip(),
                company=form.company.data.strip(),
                bio=form.bio.data.strip(),
                website=form.website.data.strip()
            )
            flash("Message Posted",'success')
            return redirect(url_for('index'))
    return render_template('addform.html',form=form)


@login_required
@app.route('/<int:post_id>')
def view_post(post_id):
    posts = models.Post.select().where(models.Post.id == post_id)
    if posts.count() == 0:
        abort(404)
    return render_template('stream.html',stream=posts)

@app.route('/follow/<userid>')
@login_required
def follow(userid):
    try:
        to_user = models.Writer.get(models.Writer.id == userid)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.create(
                from_user =g.user._get_current_object(),
                to_user=to_user
            )
        except models.IntegrityError:
            pass
        else:
            flash('''You're now following {}!'''.format(to_user.name),"success")
    return redirect(url_for('stream',userid=to_user.id))

@app.route('/unfollow/<userid>')
@login_required
def unfollow(userid):
    try:
        to_user = models.Writer.get(models.Writer.id==userid)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.get(
                from_user =g.user._get_current_object(),
                to_user=to_user).delete_instance()
        except models.IntegrityError:
            pass
        else:
            flash('''You've unfollowed {}!'''.format(to_user.name),"success")
    return redirect(url_for('stream',userid=to_user.id))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
                username='jaredshulman',
                email='shulman.jared@gmail.com',
                password='chivas31090',
            admin=True)
    except ValueError:
        pass
    app.run(debug=DEBUG,host=HOST,port=PORT)
