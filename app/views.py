from django.shortcuts import render,redirect,get_object_or_404
from . models import *
from django.contrib import messages
from django.db.models import Q
from django.db import connection
import random 
from django.db.models import Sum, Count, Min
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMessage
import datetime
#from .forms import *
from qrcode import *
import time
def home(request):
	detail=User_Detail.objects.all().order_by('-id')
	a = File_Type.objects.all().order_by('-id')[:6]   
	return render(request,'index.html',{'detail':detail,'a':a})
def register(request):
	if request.method == 'POST':
		name = request.POST.get('name')
		email = request.POST.get('email')
		mobile = request.POST.get('mobile')
		username = request.POST.get('username')
		password = request.POST.get('password')
		address = request.POST.get('address')
		user_type = request.POST.get('bio')
		bio = request.POST.get('user_type')
		image = request.FILES['img']
		if request.POST.get('user_type') == 'Editor':
			crt = Editor_Detail.objects.create(name=name,email=email,mobile=mobile,username=username,
			password=password,address=address,image=image,bio=bio)
			if crt:
				messages.success(request,'Registered Successfully')
		else:
			crt = User_Detail.objects.create(name=name,email=email,mobile=mobile,username=username,
			password=password,address=address,image=image,bio=bio)
			if crt:
				messages.success(request,'Registered Successfully')
	return render(request,'register.html',{})
def user_login(request):
	if request.session.has_key('username'):
		return redirect("user_dashboard")
	elif request.session.has_key('editor'):
		return redirect("user_dashboard")
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password =  request.POST.get('password')
			user_type = request.POST.get('user_type')
			if request.POST.get('user_type') == 'Editor':
				post = Editor_Detail.objects.filter(username=username,password=password)
				if post:
					username = request.POST.get('username')
					request.session['editor'] = username
					a = request.session['editor']
					sess = Editor_Detail.objects.only('id').get(username=a).id
					request.session['editor_id']=sess
					uid=request.session['editor_id']
					cursor=connection.cursor()
					sql=''' SELECT e.image,e.id from app_editor_detail as e where e.id='%d' ''' % (int(uid))
					post=cursor.execute(sql)
					row=cursor.fetchone()
					edit_img = row[0]
					request.session['edit_img'] = edit_img
					request.session['user_type']=user_type
					return redirect("user_dashboard")
				else:
					messages.success(request, 'Invalid Username or Password')
			else:
				post = User_Detail.objects.filter(username=username,password=password)
				if post:
					username = request.POST.get('username')
					request.session['username'] = username
					a = request.session['username']
					sess = User_Detail.objects.only('id').get(username=a).id
					request.session['user_id']=sess
					uid=request.session['user_id']
					cursor=connection.cursor()
					sql=''' SELECT u.image,u.id from app_user_detail as u where u.id='%d' ''' % (int(uid))
					post=cursor.execute(sql)
					row=cursor.fetchone()
					edit_img = row[0]
					request.session['edit_img'] = edit_img
					request.session['user_type']=user_type
					return redirect("user_dashboard")
				else:
					messages.success(request, 'Invalid Username or Password')
	return render(request,'login.html',{})
def user_dashboard(request):
	if request.session.has_key('username'):
		return render(request,'user_dashboard.html',{})
	elif request.session.has_key('editor'):
		return render(request,'user_dashboard.html',{})
	else:
		return render(request,'login.html',{})
def logout(request):
	try:
		del request.session['username']
		del request.session['user_id']
	except:
		pass
	return render(request, 'login.html', {})
def editor_logout(request):
	try:
		del request.session['editor']
		del request.session['editor_id']
	except:
		pass
	return render(request, 'login.html', {})
def add_file(request):
	if request.session.has_key('editor'):
		uid = request.session['editor_id']
		user_id = Editor_Detail.objects.get(id=int(uid))
		if request.method == 'POST':
			title = request.POST.get('title')
			category = request.POST.get('category')
			description = request.POST.get('description')
			price = request.POST.get('price')
			time = request.POST.get('time')
			sdate = request.POST.get('sdate')
			edate = request.POST.get('edate')
			project_type = request.POST.get('project_type')
			image = request.FILES['img']
			crt = File_Type.objects.create(title=title,user_id=user_id,category=category,
			image=image,description=description,price=price,time=time,sdate=sdate,edate=edate,project_type=project_type)
			if crt:
				messages.success(request, 'Added Successfully.')
		return render(request,'add.html',{})
	else:
		return render(request,'login.html',{})
def view_file(request):
	if request.session.has_key('editor'):
		uid = request.session['editor_id']
		detail=File_Type.objects.filter(user_id=int(uid)).order_by('-id')
		return render(request,'view_file.html',{'detail':detail})
	else:
		return render(request,'login.html',{})
def single_file(request,pk):
	if request.session.has_key('username'):
		uid = request.session['user_id']
		detail=File_Type.objects.filter(id=pk)
		return render(request,'single_file.html',{'detail':detail})
	elif request.session.has_key('editor'):
		uid = request.session['editor_id']
		detail=File_Type.objects.filter(id=pk)
		return render(request,'single_file.html',{'detail':detail})
	else:
		return render(request,'login.html',{})
def all_files(request,pk):
	if request.session.has_key('username'):
		uid = request.session['user_id']
		detail=File_Type.objects.filter(user_id=pk)
		return render(request,'all_files.html',{'detail':detail})
	elif request.session.has_key('editor'):
		uid = request.session['editor_id']
		detail=File_Type.objects.filter(user_id=pk)
		return render(request,'all_files.html',{'detail':detail})
	else:
		return render(request,'login.html',{})
def give_request(request,pk):
	if request.session.has_key('username'):
		uid = request.session['user_id']
		user_id=User_Detail.objects.get(id=int(uid))
		file_id=File_Type.objects.get(id=pk)
		exist = All_Request.objects.filter(user_id=user_id,file_id=file_id)
		if exist:
			messages.success(request, 'Request Already Sent.')
		else:
			detail=All_Request.objects.create(user_id=user_id,file_id=file_id,status='Pending')
			if detail:
				messages.success(request, 'Your Request Has been Sent.. Wait For Editor  Approval..')
		return render(request,'give_request.html',{})
	else:
		return render(request,'login.html',{})
def requested_files(request):
	if request.session.has_key('editor'):
		uid = request.session['editor_id']
		detail=All_Request.objects.filter(file_id__in=File_Type.objects.filter(user_id=int(uid)))
		return render(request,'requested_files.html',{'detail':detail})
	else:
		return render(request,'login.html',{})
def accept(request,pk):
	if request.session.has_key('editor'):
		uid = request.session['editor_id']
		detail=All_Request.objects.filter(id=pk).update(status='Accepted')
		return redirect('requested_files')
	else:
		return render(request,'login.html',{})
def reject(request,pk):
	if request.session.has_key('editor'):
		uid = request.session['editor_id']
		detail=All_Request.objects.filter(id=pk).update(status='Declined')
		return redirect('requested_files')
	else:
		return render(request,'login.html',{})
def user_files(request):
	if request.session.has_key('username'):
		uid = request.session['user_id']
		detail=All_Request.objects.filter(user_id=int(uid))
		return render(request,'user_files.html',{'detail':detail})
	else:
		return render(request,'login.html',{})
def all_learn_file(request):
	if request.session.has_key('username'):
		uid = request.session['user_id']
		detail=Learn_Material.objects.all().order_by('-id')
		return render(request,'all_learn_file.html',{'detail':detail})
	elif request.session.has_key('editor'):
		uid = request.session['editor_id']
		detail=Learn_Material.objects.all().order_by('-id')
		return render(request,'all_learn_file.html',{'detail':detail})
	else:
		return render(request,'login.html',{})
def single_learn(request,pk):
	if request.session.has_key('username'):
		uid = request.session['user_id']
		detail=Learn_Material.objects.filter(id=pk)
		return render(request,'single_learn.html',{'detail':detail})
	elif request.session.has_key('editor'):
		uid = request.session['editor_id']
		detail=Learn_Material.objects.filter(id=pk)
		return render(request,'single_learn.html',{'detail':detail})
	else:
		return render(request,'login.html',{})
def about(request):
	return render(request,'about.html',{})
def terms(request):
	return render(request,'terms.html',{})
def faq(request):
	detail=FAQ.objects.all().order_by('-id')
	return render(request,'faq.html',{'detail':detail})
def message(request):
	if request.session.has_key('username'):
		uid = request.session['user_id']
		email=request.GET.get('email')
		if request.method == 'POST':
			name=request.POST.get('name')
			email = request.POST.get('email')
			mobile = request.POST.get('mobile')
			subject = request.POST.get('subject')
			message = request.POST.get('message')
			from django.core.mail import EmailMultiAlternatives
			email_from = settings.EMAIL_HOST_USER
			subject = subject
			text_content = "Message Sent By User"
			html_content = "<p>Name:" + name + "</p><p>Email:"+email+"</p><p>Mobile:"+mobile+"</p><p>Message:"+message+"</p>"
			msg = EmailMultiAlternatives(subject, text_content, email_from, [email])
			msg.attach_alternative(html_content, "text/html")
			msg.send()
			if msg:
				messages.success(request,'Message Successfully Sent.')
		return render(request,'message.html',{})
	else:
		return render(request,'login.html',{})
def search(request):
	if request.session.has_key('username'):
		uid = request.session['user_id']
		if request.method == 'POST':
			a = request.POST.get('search')
			if a:
				detail=File_Type.objects.filter(Q(title__icontains=a) | Q(category__icontains=a))
				return render(request,'search.html',{'detail':detail})
		return render(request,'search.html',{})
	elif request.session.has_key('editor'):
		uid = request.session['editor_id']
		if request.method == 'POST':
			a = request.POST.get('search')
			if a:
				detail=File_Type.objects.filter(Q(title__icontains=a) | Q(category__icontains=a))
				return render(request,'search.html',{'detail':detail})
		return render(request,'search.html',{})
	else:
		return render(request,'login.html',{})
def chat_editor(request,pk):
	if request.session.has_key('editor'):
		file_id=File_Type.objects.get(id=pk)
		if request.method == 'POST':
			a=request.POST.get('chat')
			name = request.session['editor']
			detail=Chat.objects.create(name=name,file_id=file_id,question=a)
		chat_id=Chat.objects.filter(file_id=pk)
		return render(request,'chat_editor.html',{'chat_id':chat_id})
	else:
		return render(request,'login.html',{})
def chat_user(request,pk):
	if request.session.has_key('username'):
		file_id=File_Type.objects.get(id=pk)
		if request.method == 'POST':
			a=request.POST.get('chat')
			name = request.session['username']
			detail=Chat.objects.create(name=name,file_id=file_id,question=a)
		chat_id=Chat.objects.filter(file_id=pk)
		return render(request,'chat_user.html',{'chat_id':chat_id})
	else:
		return render(request,'login.html',{})
def delete(request,pk):
	crt=File_Type.objects.filter(id=pk).delete()
	return redirect('view_file')
def profile_page(request):
	if request.session.has_key('username'):
		user_id = request.session['user_id']
		uid = User_Detail.objects.get(id=int(user_id))
		if FreelancerProfile.objects.filter(user_id=int(user_id)).exists():
			row = FreelancerProfile.objects.filter(user_id=int(user_id))
			return render(request,'view_profile.html',{'row':row})
		else:
			if request.method == 'POST':
				biography = request.POST.get('biography')
				skills = request.POST.get('skills')
				experience = request.POST.get('experience')
				portfolio_link = request.POST.get('portfolio_link')
				availability = request.POST.get('availability')
				crt = FreelancerProfile.objects.create(biography=biography,skills=skills,experience=experience,
				portfolio_link=portfolio_link,availability=availability,user_id=uid)
				if crt:
					return render(request,'view_profile.html',{})
			return render(request,'profile.html',{})
	else:
		return render(request,'login.html',{})
def single_profile(request,pk):
	user_id = request.session['user_id']
	row = FreelancerProfile.objects.filter(user_id=int(user_id))
	return render(request,'single_profile.html',{'row':row})
def give_request_user(request,pk):
	if request.session.has_key('username'):
		free_id = request.session['user_id']
		uid = User_Detail.objects.get(id=int(free_id))
		job_id = File_Type.objects.get(id=pk)
		user_id = request.GET.get('id')
		editor_id = Editor_Detail.objects.get(id=int(user_id))
		if request.method == 'POST':
			msg = request.POST.get('msg')
			crt=RequestProject.objects.create(user_id=editor_id,job_id=job_id,freelancer_id=uid,
			job_status='Pending',msg=msg,project_status='Pending')
			if crt:
				messages.success(request,'Request Sent Successfully.')
		return render(request,'give_request_user.html',{})
	else:
		return render(request,'login.html',{})
def all_files_project(request):
	if request.session.has_key('username'):
		free_id = request.session['user_id']
		row = RequestProject.objects.filter(freelancer_id=int(free_id))
		return render(request,'files.html',{'row':row})
	else:
		return render(request,'login.html',{})
def free_job_detail(request):
	if request.session.has_key('editor'):
		free_id = request.session['editor_id']
		row = RequestProject.objects.filter(user_id=int(free_id))
		return render(request,'free_job_detail.html',{'row':row})
	else:
		return render(request,'login.html',{})
def accept(request,pk):
	if request.session.has_key('editor'):
		free_id = request.session['editor_id']
		if request.method == 'POST':
			reply = request.POST.get('reply')
			delivery_date = request.POST.get('delivery_date')
			crt = RequestProject.objects.filter(id=pk).update(job_status="Accepted",reply=reply,delivery_date=delivery_date)
			return redirect('free_job_detail')
		return render(request,'accept.html',{})
	else:
		return render(request,'login.html',{})
def reject(request,pk):
	if request.session.has_key('editor'):
		free_id = request.session['editor_id']
		return redirect('free_job_detail')
	else:
		return render(request,'login.html',{})
def all_acc_proj(request):
	if request.session.has_key('editor'):
		free_id = request.session['editor_id']
		row=RequestProject.objects.filter(user_id=int(free_id),job_status='Accepted')
		return render(request,'all_acc_proj.html',{'row':row})
	else:
		return render(request,'login.html',{})
def payment(request,pk):
	if request.session.has_key('editor'):
		from datetime import date
		current_date = date.today()
		free_id = request.session['editor_id']
		job_id = RequestProject.objects.get(id=pk)
		if request.method == 'POST':
			payment_amount = request.POST.get('payment_amount')
			crt = Payment.objects.create(req_id=job_id,payment_amount=payment_amount,payment_date=current_date,
			payment_status="Paid")
			if crt:
				return render(request,'success.html',{})
		return render(request,'payment.html',{})
	else:
		return render(request,'login.html',{})
def payment_list(request):
	if request.session.has_key('editor'):
		free_id = request.session['editor_id']
		row = Payment.objects.filter(req_id__in=RequestProject.objects.filter(user_id=int(free_id)))
		total_paid = 0
		for i in row:
			total_paid += int(i.payment_amount)
		return render(request,'payment_list.html',{'row':row,'total_paid':total_paid})
	else:
		return render(request,'login.html',{})


from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
def train_knn_model():
    # Fetch all categories
    files = File_Type.objects.all()
    categories = [file.category for file in files]
    
    # Vectorize categories using TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(categories)
    
    # Train KNN
    knn = NearestNeighbors(n_neighbors=5, metric='cosine').fit(tfidf_matrix)
    
    return knn, vectorizer, files

def search_with_knn(query, knn_model, vectorizer, files):
    # Vectorize query
    query_vector = vectorizer.transform([query])
    
    # Find nearest neighbors
    distances, indices = knn_model.kneighbors(query_vector)
    
    # Get results
    results = [(files[idx], distances[0][i]) for i, idx in enumerate(indices[0])]
    return results

knn_model, vectorizer, files = train_knn_model()

def knn_search_view(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = search_with_knn(query, knn_model, vectorizer, files)

    return render(request, 'search.html', {'query': query, 'results': results})
def ml_search_view(request):
    query = request.GET.get('q', '')  # Get the search query
    results = []

    if query:
        model = SentenceTransformer('all-MiniLM-L6-v2')  # Load the pretrained model
        query_embedding = model.encode(query)  # Convert query to embedding

        # Retrieve and calculate similarity
        all_files = File_Type.objects.exclude(category_embedding__isnull=True)  # Ensure embeddings exist
        file_similarities = []

        for file in all_files:
            category_embedding = np.frombuffer(file.category_embedding, dtype=np.float32)
            similarity = np.dot(query_embedding, category_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(category_embedding)
            )
            file_similarities.append((file, similarity))

        # Sort files by similarity
        file_similarities.sort(key=lambda x: x[1], reverse=True)
        results = [file for file, sim in file_similarities[:10]]  # Get top 10 results

    return render(request, 'search.html', {'query': query, 'results': results})
def freencler_payment(request):
	if request.session.has_key('user_id'):
		free_id = request.session['user_id']
		row = Payment.objects.filter(req_id__in=RequestProject.objects.filter(freelancer_id=int(free_id)))
		return render(request,'freencler_payment.html',{'row':row})
	else:
		return render(request,'login.html',{})
def freelancer_proj(request):
	if request.session.has_key('user_id'):
		free_id = request.session['user_id']
		row = RequestProject.objects.filter(freelancer_id=int(free_id))
		return render(request,'freelancer_proj.html',{'row':row})
	else:
		return render(request,'login.html',{})
def update_status(request,pk):
	if request.session.has_key('user_id'):
		free_id = request.session['user_id']
		if request.method == 'POST':
			project_status =  request.POST.get('project_status')
			row = RequestProject.objects.filter(id=pk).update(project_status=project_status)
			if row:
				return redirect('freelancer_proj')
		return render(request,'update_status.html',{})
	else:
		return render(request,'login.html',{})
def group_proj(request):
	if request.session.has_key('user_id'):
		free_id = request.session['user_id']
		row = RequestProject.objects.filter(freelancer_id=int(free_id),job_status='Accepted',job_id__in=File_Type.objects.filter(project_type='Group Project'))
		return render(request,'group_proj.html',{'row':row})
	else:
		return render(request,'login.html',{})
def view_group_proj(request,pk):
	if request.session.has_key('user_id'):
		free_id = request.session['user_id']
		row = RequestProject.objects.filter(job_id=pk)
		return render(request,'view_group_proj.html',{'row':row})
	else:
		return render(request,'login.html',{})
def user_group_proj(request):
	if request.session.has_key('editor_id'):
		free_id = request.session['editor_id']
		row = RequestProject.objects.filter(user_id=int(free_id),job_status='Accepted',job_id__in=File_Type.objects.filter(project_type='Group Project'))
		return render(request,'user_group_proj.html',{'row':row})
	else:
		return render(request,'login.html',{})
def user_view_group_proj(request,pk):
	if request.session.has_key('editor_id'):
		free_id = request.session['editor_id']
		row = RequestProject.objects.filter(job_id=pk)
		return render(request,'user_view_group_proj.html',{'row':row})
	else:
		return render(request,'login.html',{})


