import os
from flask import render_template, url_for, flash, redirect, request, abort,jsonify
from OfferZone import app,db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from OfferZone.models import User,Mall,Shop,Product,Offer,Gallery, Contact
from PIL import Image
from OfferZone.forms import RegistrationForm,LoginForm,AccountForm,MallRegistrationForm,ShopRegistrationForm,ProductRegistrationForm,OfferRegistrationForm,RequestResetForm,ResetPasswordForm, Imageadd, Changepassword
import json
from random import randint
from flask_mail import Message

@app.route("/")
@app.route("/pindex")
def pindex():
    form1 = LoginForm()
    form2 =RegistrationForm()
    saved_offers=ret_list=getofferList()
    gallery = Gallery.query.all()
    return render_template('pindex.html',offers=saved_offers,form1=form1,form2=form2,gal=gallery)


@app.route('/feedback',methods=['POST','GET'])
def pindexx():
    if request.method=='POST':
        name= request.form['name']
        email= request.form['email']
        message= request. form['message']
        new1 = Contact(name=name,email=email,message=message)
        try:
            db.session.add(new1)
            db.session.commit()
            return redirect('/')

        except:
            return 'not add'  
    else:
        saved_offers=ret_list=getofferList()
        gallery = Gallery.query.all()
        return render_template('pindex.html',offers=saved_offers,form1=form1,form2=form2,gal=gallery)



@app.route("/home")
@login_required
def home():
    saved_offers=ret_list=getofferList()
    return render_template('home.html',offers=saved_offers)

@app.route("/show_malls")
@login_required
def show_malls():
    saved_malls=Mall.query.all()
    return render_template("showmalls.html",malls=saved_malls)

@app.route("/show_shops")
@login_required
def show_shops():
    saved_shop=Shop.query.all()
    return render_template("showshops.html",shops=saved_shop)
@app.route("/show_offers")
def show_offers():
    saved_offer=Offer.query.all()
    return render_template("showoffers.html",saved_offer=Offers)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form1 = LoginForm()
    form2=RegistrationForm()
    user1 = User.query.filter_by(username=form2.username.data).first()
    if form2.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form2.password.data).decode('utf-8')
        user = User(username=form2.username.data, email=form2.email.data, password=hashed_password, usertype='user')
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect('/')
    return render_template('pindex.html',title='Register', form1=form1,form2=form2)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form1 = LoginForm()
    form2=RegistrationForm()
    if form1.validate_on_submit():
        user = User.query.filter_by(email=form1.email.data, usertype= 'user').first()
        user1 = User.query.filter_by(email=form1.email.data, usertype= 'admin').first()
        if user and bcrypt.check_password_hash(user.password, form1.password.data):
            login_user(user, remember=form1.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/home')

        if user1 and user1.password== form1.password.data:
            login_user(user1, remember=form1.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/admin')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('pindex.html', title='Login', form1=form1,form2=form2)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')

@app.route("/account", methods=['GET', 'POST'])
def account():
    form=AccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


    

def save_picture(form_picture):
    random_hex = random_with_N_digits(14)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = str(random_hex) + f_ext
    picture_path = os.path.join(app.root_path, 'static/pics', picture_fn)
    


    output_size = (5000, 5000)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)


    return picture_fn

@app.route("/mall/new", methods=['GET', 'POST'])
def new_mall():
    form=MallRegistrationForm()
    pic=""
    if form.validate_on_submit():
        if form.image.data:
            profile_pic=save_picture(form.image.data)
            pic=profile_pic
        mall = Mall(owner=current_user.username,name=form.name.data, desc=form.desc.data, addr1=form.addr1.data,addr2=form.addr2.data,image_file=pic,latitude=form.latitude.data, Logitude =form. Logitude .data)
        db.session.add(mall)
        db.session.commit()
        flash('Mall has been created!', 'success')
        print(pic)
    saved_malls = Mall.query.filter_by(owner=current_user.username).all()
    return render_template('mall.html', title='New Mall',form=form,malls=saved_malls,pic=pic)

@app.route("/mall/<int:mall_id>/update", methods=['GET', 'POST'])
def update_mall(mall_id):
    mall = Mall.query.get_or_404(mall_id)
    form = MallRegistrationForm()
    pic=""
    if form.validate_on_submit():

        if form.image.data:
         profile_pic=save_picture(form.image.data)
         pic=profile_pic

        mall.name = form.name.data
        mall.desc=form.desc.data
        mall.addr1=form.addr1.data
        mall.addr2=form.addr2.data
        mall.image_file=pic
        mall.latitude=form.latitude.data
        mall.Logitude =form.Logitude.data
        db.session.commit()
        flash('Mall has been updated!', 'success')
        return redirect(url_for('new_mall'))
    elif request.method == 'GET':
        
        form.name.data = mall.name
        form.desc.data= mall.desc
        form.addr1.data=mall.addr1
        pic= url_for('static', filename='pics/'+mall.image_file)
        form.addr2.data=mall.addr2
        form.latitude.data=mall.latitude
        form. Logitude .data=mall. Logitude 
    # 'sho' is the backref variable of 'Mall'table..it is using to count no:of shops..
        print(mall.sho)

    saved_malls = Mall.query.filter_by(owner=current_user.username).all()
    return render_template('mall.html', title='Update Mall',
                           form=form,malls=saved_malls,action="modify",mall_id=mall_id,pic=pic)


@app.route("/mall/<int:mall_id>/delete", methods=['POST'])
@login_required
def delete_mall(mall_id):
    mall = Mall.query.get_or_404(mall_id)
    db.session.delete(mall)
    db.session.commit()
    flash('Mall has been deleted!', 'success')
    return redirect(url_for('new_mall'))



@app.route("/shop/new", methods=['GET', 'POST'])
def new_shop():
    form=ShopRegistrationForm()
    view="default.jpg"

    if form.validate_on_submit():

            if form.picture.data:
               picture_file = save_picture(form.picture.data)
               view= picture_file

            print(view)   

            mall_id=form.mall.data

            selected_mall = Mall.query.get_or_404(str(mall_id))

            shop = Shop(owner=current_user.username,name=form.name.data, addr=form.addr.data, phoneno=form.phoneno.data,
            desc=form.desc.data,category=form.category.data,malll=selected_mall,image=view)

            db.session.add(shop)
            db.session.commit()
            flash('Shop has been created!', 'success')
            print(shop)
            

            form.name.data = ""
            form.addr.data = ""
            form.phoneno.data = ""
            form.desc.data = ""

   # view= url_for('static', filename='pics/' + view)    
    saved_shop=Shop.query.filter_by(owner=current_user.username).all()
    return render_template('shop.html', title='New Shop',form=form,shops=saved_shop,view=view)


@app.route("/shop/<int:shop_id>/update", methods=['GET', 'POST'])
def update_shop(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    form = ShopRegistrationForm()
    view=""
    if form.validate_on_submit():
        
        if form.picture.data:

               picture_file = save_picture(form.picture.data)
               view= picture_file

        shop.name = form.name.data
        shop.addr=form.addr.data
        shop.phoneno=form.phoneno.data
        shop.desc=form.desc.data
        shop.image=view

        
        mall_id=form.mall.data

        selected_mall = Mall.query.get_or_404(str(mall_id))

        
        shop.category=form.category.data
        shop.mall=selected_mall
        db.session.commit()
        flash('shop has been updated!', 'success')
        return redirect(url_for('new_shop'))
    elif request.method == 'GET':
        
        form.name.data = shop.name
        form.addr.data= shop.addr
        form.phoneno.data=shop.phoneno
        form.desc.data=shop.desc
        form.category.data=shop.category
        print(shop.category)
       
        
    view= url_for('static', filename='pics/'+shop.image)
    saved_shop=Shop.query.filter_by(owner=current_user.username).all()
    return render_template('shop.html', title='Update shop',
                           form=form,shops=saved_shop,action="modify",shop_id=shop_id,view=view)



@app.route("/shop/<int:shop_id>/delete", methods=['POST'])
@login_required
def delete_shop(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    db.session.delete(shop)
    db.session.commit()
    flash('Shop has been deleted!', 'success')
    return redirect(url_for('new_shop'))

@app.route('/shop/<o>',methods = ['GET','POST'])
def index(o):
    user=Shop.query.filter_by(name=o).first()
    if user is None:
        return '<h2>not found'
    else:
        return render_template('simple.html',ab=user.catag)


    

@app.route("/product/new",methods = ['GET','POST'])
def new_product():
    form=ProductRegistrationForm()
    view="default.jpg"

    if form.validate_on_submit():

        if form.pic.data:
            pic_file = save_picture(form.pic.data)
            view = pic_file
        print(view)  

        shop_id=form.shop.data
        selected_shop = Shop.query.get_or_404(str(shop_id))
    
        product = Product(owner1=current_user.username,name=form.name.data, owner=form.owner.data, price=form.price.data, desc=form.desc.data,shop=selected_shop,img=view )
       
        db.session.add(product)
        db.session.commit()
        print(product)
        flash('product has been created')
        return redirect(url_for('new_product'))
            
    saved_product=Product.query.filter_by(owner1=current_user.username).all()
    return render_template('product.html',form=form ,title='New Product',products=saved_product,view=view)
    



    
   

    
@app.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductRegistrationForm()
    view=""
    if form.validate_on_submit():
        
         if form.pic.data:
            pic_file = save_picture(form.pic.data)
            view = pic_file

       

         product.name = form.name.data
         product.owner=form.owner.data
         product.price=form.price.data
         product.desc=form.desc.data
         product.img=view
           
         shop_id=form.shop.data
         selected_shop = Shop.query.get_or_404(str(shop_id))
         product.shop=selected_shop 
         
         db.session.commit()

         flash('Product has been updated!', 'success')
         return redirect(url_for('new_product'))
    elif request.method == 'GET':
        
        form.name.data = product.name
        form.owner.data= product.owner
        form.price.data=product.price
        form.desc.data=product.desc
        view= url_for('static', filename='pics/'+product.img)
        form.shop.data=product.shopid
        print (product.shopid)

    saved_product=Product.query.filter_by(owner1=current_user.username).all()
    return render_template('product.html', title='Update Product',
                           form=form,products=saved_product,action="modify",product_id=product_id,view=view)





@app.route("/product/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product has been deleted!', 'success')
    return redirect(url_for('new_product'))

@app.route('/product/<k>',methods = ['GET','POST'])
def pro(k):
    user=Product.query.filter_by(name=k).first()
    if user is None:
        return '<h2>not found'
    else:
        return render_template('pro.html',ab=user.company,bc=user.price)


@app.route("/new_offers")
def new_offers():
    saved_offers=ret_list=getofferList()
    return render_template('new_offers.html',offers=saved_offers)


@app.route("/new_off")
def new_off():
    return redirect(url_for('home'))



@app.route("/offer/new",methods = ['GET','POST'])
def new_offer():
    form=OfferRegistrationForm()
    model=""
    if form.validate_on_submit():
        if form.pic.data:
            profile=save_picture(form.pic.data)
            model=profile
        product_id=form.product.data
       
        selected_product = Product.query.get_or_404(str(product_id))
        
        dis=(Product.price-500)/5
        offer = Offer(owner=current_user.username,name=form.name.data, price=form.price.data, desc=form.desc.data, product=selected_product,dis=form.dis.data,image=model )
        
        db.session.add(offer)
        db.session.commit()
        print(offer)
        print(model)
        flash('offer has been created')
    
    saved_offer=Offer.query.filter_by(owner=current_user.username).all()
    return render_template('offer.html',form=form ,title='New Offer',offers=saved_offer,model=model)

@app.route("/offer/<int:offer_id>/update", methods=['GET', 'POST'])
def update_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    form = OfferRegistrationForm()
    model=""
    if form.validate_on_submit():
        if form.pic.data:
            profile=save_picture(form.pic.data)
            model=profile
        offer.name = form.name.data
        offer.price=form.price.data
        offer.desc=form.desc.data
        offer.dis=form.dis.data
        offer.image=model
        db.session.commit()
        flash('Offer has been updated!', 'success')
        return redirect(url_for('new_offer'))
    elif request.method == 'GET':
        
        form.name.data = offer.name
        form.price.data= offer.price
        form.desc.data=offer.desc
        form.dis.data=offer.dis
        model= url_for('static', filename='pics/'+offer.image)
        form.product.data=offer.productid
        print (offer.productid)
    
    saved_offer=Offer.query.filter_by(owner=current_user.username).all()
    return render_template('offer.html', title='Update Offer',
                           form=form,offers=saved_offer,action="modify",offer_id=offer_id,model=model)



@app.route("/offer/<int:offer_id>/delete", methods=['POST'])
@login_required
def delete_offer(offer_id):
    offer =Offer.query.get_or_404(offer_id)
    db.session.delete(offer)
    db.session.commit()
    flash('offer has been deleted!', 'success')
    return redirect(url_for('new_offer'))


@app.route("/hello",methods =['GET','POST'])
def hello():
    #malls = Mall.query.all()
    #json_data=jsonify(json_list = malls)
    tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
    ]
    #print(json_data)
    return jsonify({'tasks': tasks})



@app.route("/checkuser",methods =['GET','POST'])
def login_me():

    #get request code under or below

    #username = request.args.get('username')
    #password = request.args.get('password')
    
   #working:this r post methode below...if any error this code will araise "GET REQUEST"
    
    retstring="GET REQUEST"
    # if this r get request method..that is showing "GET REQUEST"...this r error
    try:
        if request.method == 'POST':
            username= request.form['username']
            password=request.form['password']
            #username,password were andriod variables.

    #after successfull post method,typing user name ,password,it is not in db.araise "invalid user"
            retstring="Invalid User"

            user = User.query.filter_by(email=username).first()
            #android r typing 'email' in mobile as space for 'username'... that 'username' in python variable...
            if user and bcrypt.check_password_hash(user.password,password):
                retstring="Welcome "+user.username
    except Exception as e:
        retstring="Error"

    return retstring

@app.route("/getoffers",methods =['GET','POST'])
def getoffers():
    ret_list=getofferList()
    return json.dumps(ret_list)
   

def getofferList():
    malls=Mall.query.all()
    ret_list=[]
    i=0
    for mall in malls:
        for shop in mall.sho:
            for product in shop.pro:
                    for offer in product.offers:
                        discount_per=round(((float(product.price)-float(offer.price))/float(product.price))*100)
                        thisdict = {
                                "product": product.name,
                                "mall": mall.name,
                                "shop": shop.name,
                                "old_price":product.price,
                                "new_price":offer.price,
                                "offer_per":int(discount_per),
                                "image":url_for('static', filename='pics/' + product.img),
                                "lat":mall.latitude,
                                "log":mall.Logitude,
                                "d":i
                                }
                        i=i+1
                        ret_list.append(thisdict)
    return ret_list



#@app.route("/new_register",methods =['GET','POST'])
#def new_register():

   
    
  #  error="GET REQUEST"
    
       # if request.method == 'POST':
         #   username= request.form['username']
         #   email= request.form['email']

         #   password=request.form['password']
       # confirm password=request.form['confirm password']
 # username,password,email,confirm password were andriod variables.



@app.route("/newregister",methods =['GET','POST'])
def register_me():
    retstring="OKAY"
    username=""
    password=""
    email=""
   
    try:
        if request.method == 'POST':
            username= request.form['username']
            password=request.form['password']
            email=request.form['email']
           
        else:
            username = request.args.get('username')
            password = request.args.get('password')
            email=request.args.get('email')
           
        user = User.query.filter_by(username=username).first()
        if user:
            retstring='That username is taken. Please choose a different one.'
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                retstring='That email is taken. Please choose a different one.'

        if(retstring=="OKAY"):  #If Username and Email not exists
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(username=username, email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            retstring='Success'
        
    except Exception as e:
        print(e)
        retstring="Error"

    return retstring




@app.route("/getnearestoffers",methods =['GET','POST'])
def getnearestOffers():
    ret_list=getofferList()
    lat=0
    lon=0
    
    
    if request.method == 'POST':
        lat= request.form['lat']
        lon=request.form['lon']
        
    if(lat>0  and lon>0):
        for offer in ret_list:
            try:
                lat1=float(offer["lat"])
                lon1=float(offer["lon"])
                d=distance(lat,lon,lat1,lon1)
                offer["d"]=d
            except Exception as e:
                 pass
               
    
    sorted_list=sorted(ret_list, key = lambda i: i['d'],reverse=False)
    return json.dumps(sorted_list)

def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(a))





def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('resettoken', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)




@app.route("/resetrequest", methods=['GET', 'POST'])
def resetrequest():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect('/login')
    return render_template('resetrequest.html', title='Reset Password', form=form)




@app.route("/resetpassword/<token>", methods=['GET', 'POST'])
def resettoken(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect('/resetrequest')
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect('/login')
    return render_template('resetpassword.html', title='Reset Password', form=form)






@app.route('/admin')
@login_required
def admin():
    return render_template("admin.html")


@app.route('/aimageadd',methods=['POST','GET'])
@login_required
def aimageadd():
    form=Imageadd()
    view="default.jpg"

    if form.validate_on_submit():

        if form.pic.data:
            pic_file = save_picture(form.pic.data)
            view = pic_file
        print(view)  
    
        gallery = Gallery(name=form.name.data,img=view )
       
        db.session.add(gallery)
        db.session.commit()
        print(gallery)
        flash('image added')
        return redirect('/galleryview')
            
    return render_template('aimageadd.html',form=form)

@app.route('/galleryview')
@login_required
def galleryview():
    gallery = Gallery.query.all()
    return render_template('galleryview.html',gallery=gallery)

@app.route("/view/<int:id>", methods=['GET', 'POST'])
@login_required
def aimageupdate(id):
    gallery = Gallery.query.get_or_404(id)
    form = Imageadd()
    if form.validate_on_submit():
        if form.pic.data:
            picture_file = save_picture(form.pic.data)
            gallery.img = picture_file
        gallery.name = form.name.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect('/galleryview')
    elif request.method == 'GET':
        form.name.data = gallery.name
    image_file = url_for('static', filename='pics/' + gallery.img)
    return render_template('aimageupdate.html',form=form)
                           
@app.route("/view/<int:id>/delete")
@login_required
def deleteimage(id):
    gallery =Gallery.query.get_or_404(id)
    db.session.delete(gallery)
    db.session.commit()
    flash('image has been deleted!', 'success')
    return redirect('/galleryview')

@app.route('/userview')
@login_required
def userview():
    user=User.query.filter_by(usertype='user').all()
    return render_template('userview.html',user=user)

@app.route('/mallview')
@login_required
def mallview():
    mall= Mall.query.all()
    return render_template('mallview.html',mall=mall)

@app.route('/mallupdate/<int:mall_id>',methods=['POST','GET'])
@login_required
def mallupdate(mall_id):
    mall = Mall.query.get_or_404(mall_id)
    form = MallRegistrationForm()
    pic=""
    if form.validate_on_submit():

        if form.image.data:
         profile_pic=save_picture(form.image.data)
         pic=profile_pic

        mall.name = form.name.data
        mall.desc=form.desc.data
        mall.addr1=form.addr1.data
        mall.addr2=form.addr2.data
        mall.image_file=pic
        mall.latitude=form.latitude.data
        mall.Logitude =form.Logitude.data
        db.session.commit()
        flash('Mall has been updated!', 'success')
        return redirect('/mallview')
    elif request.method == 'GET':
        
        form.name.data = mall.name
        form.desc.data= mall.desc
        form.addr1.data=mall.addr1
        pic= url_for('static', filename='pics/'+mall.image_file)
        form.addr2.data=mall.addr2
        form.latitude.data=mall.latitude
        form. Logitude .data=mall. Logitude 
    return render_template('mallupdate.html', 
                           form=form,action="modify",mall_id=mall_id,pic=pic,mall=mall)


@app.route("/malldelete/<int:mall_id>", methods=['POST'])
@login_required
def deletemall(mall_id):
    mall = Mall.query.get_or_404(mall_id)
    db.session.delete(mall)
    db.session.commit()
    flash('Mall has been deleted!', 'success')
    return redirect('/mallview')


@app.route('/shopview')
@login_required
def shopview():
    shop= Shop.query.all()
    return render_template('shopview.html',shop=shop)

@app.route("/shopupdate/<int:shop_id>", methods=['GET', 'POST'])
@login_required
def shopupdate(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    form = ShopRegistrationForm()
    view=""
    if form.validate_on_submit():
        
        if form.picture.data:

               picture_file = save_picture(form.picture.data)
               view= picture_file

        shop.name = form.name.data
        shop.addr=form.addr.data
        shop.phoneno=form.phoneno.data
        shop.desc=form.desc.data
        shop.image=view

        
        mall_id=form.mall.data

        selected_mall = Mall.query.get_or_404(str(mall_id))

        
        shop.category=form.category.data
        shop.mall=selected_mall
        db.session.commit()
        flash('shop has been updated!', 'success')
        return redirect('/shopview')
    elif request.method == 'GET':
        
        form.name.data = shop.name
        form.addr.data= shop.addr
        form.phoneno.data=shop.phoneno
        form.desc.data=shop.desc
        form.category.data=shop.category
        print(shop.category)
    view= url_for('static', filename='pics/'+shop.image)
    return render_template('shopupdate.html', title='Update shop',
                           form=form,action="modify",shop_id=shop_id,view=view,shop=shop)


@app.route("/shopdelete/<int:shop_id>", methods=['POST'])
@login_required
def deleteshop(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    db.session.delete(shop)
    db.session.commit()
    flash('Shop has been deleted!', 'success')
    return redirect('/shopview')


@app.route('/productview')
@login_required
def productview():
    product= Product.query.all()
    return render_template('productview.html',product=product)

@app.route("/productupdate/<int:product_id>", methods=['GET', 'POST'])
@login_required
def updateproduct(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductRegistrationForm()
    view=""
    if form.validate_on_submit():
        
         if form.pic.data:
            pic_file = save_picture(form.pic.data)
            view = pic_file

       

         product.name = form.name.data
         product.owner=form.owner.data
         product.price=form.price.data
         product.desc=form.desc.data
         product.img=view
           
         shop_id=form.shop.data
         selected_shop = Shop.query.get_or_404(str(shop_id))
         product.shop=selected_shop 
         
         db.session.commit()

         flash('Product has been updated!', 'success')
         return redirect('/productview')
    elif request.method == 'GET':
        
        form.name.data = product.name
        form.owner.data= product.owner
        form.price.data=product.price
        form.desc.data=product.desc
        view= url_for('static', filename='pics/'+product.img)
        form.shop.data=product.shopid
    return render_template('productupdate.html', title='Update Product',
                           form=form,action="modify",product_id=product_id,pic=view,product=product)

@app.route("/productdelete/<int:product_id>", methods=['POST'])
@login_required
def deleteproduct(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product has been deleted!', 'success')
    return redirect('/productview')


@app.route('/offerview')
@login_required
def offerview():
    offer = Offer.query.all()
    return render_template('offerview.html',offer=offer)


@app.route("/offerupdate/<int:offer_id>", methods=['GET', 'POST'])
@login_required
def updateoffer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    form = OfferRegistrationForm()
    model=""
    if form.validate_on_submit():
        if form.pic.data:
            profile=save_picture(form.pic.data)
            model=profile
        offer.name = form.name.data
        offer.price=form.price.data
        offer.desc=form.desc.data
        offer.dis=form.dis.data
        offer.image=model
        db.session.commit()
        flash('Offer has been updated!', 'success')
        return redirect('/offerview')
    elif request.method == 'GET':
        
        form.name.data = offer.name
        form.price.data= offer.price
        form.desc.data=offer.desc
        form.dis.data=offer.dis
        model= url_for('static', filename='pics/'+offer.image)
        form.product.data=offer.productid
    return render_template('offerupdate.html', title='Update Offer',
                           form=form,action="modify",offer_id=offer_id,pic=model,offer=offer)

@app.route("/offerdelete/<int:offer_id>", methods=['POST'])
@login_required
def deleteoffer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    db.session.delete(offer)
    db.session.commit()
    flash('Offer has been deleted!', 'success')
    return redirect('/offerview')


@app.route('/feedbackview')
@login_required
def feedbackview():
    feedback=Contact.query.all()
    return render_template('feedback.html',feedback=feedback)

@app.route("/adminaccount", methods=['GET', 'POST'])
@login_required
def adminaccount():
    form=AccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect("")
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='pics/' + current_user.image_file)
    return render_template('adminaccount.html', title='Account',
                           image_file=image_file, form=form)


@app.route('/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    form = Changepassword()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        logout_user()
        flash('Your Password Has Been Changed')
        return redirect('/login')
    elif request.method == 'GET':
        hashed_password = current_user.password  
    return render_template('changepassword.html', form=form)