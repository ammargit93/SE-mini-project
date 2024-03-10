import json
import requests
from flask import *
from config import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecretkey'


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/about-us")
def about():
    return render_template('about-us.html')


def update_database(data):
    with open('data/qna.json', 'w') as f:
        json.dump(data, f, indent=2)


@app.route("/qna", methods=['GET', 'POST'])
def qna():
    if 'username' in session:
        if request.method == 'POST':
            if 'title' in request.form:
                new_question = {
                    "id": qna_collection.count_documents({}) + 1,
                    "title": request.form.get('title'),
                    "content": request.form.get('question'),
                    "account": session['username'],
                    "replies": []
                }
                qna_collection.insert_one(new_question)

            if 'form-type' in request.form:
                question_id = int(request.form.get('question_id', -1))
                reply_content = request.form.get('replyContent')
                if question_id != -1:
                    question = qna_collection.find_one({'id': question_id})
                    if question:
                        qna_collection.update_one(
                            {'id': question_id},
                            {'$push': {'replies': {"content": reply_content, "reply_account": session['username']}}}
                        )
                        return redirect(url_for('qna'))
        data = list(qna_collection.find({}))
        for d in data:
            print(d)
        return render_template('qna.html', questions=data, author_name=session['username'])

    return redirect('signup')


# recruiter posts
@app.route("/posts", methods=['GET', 'POST'])
def posts():
    if 'username' in session:
        if request.method == 'POST':
            if 'title' in request.form:
                new_question = {
                    "id": recruiter_post_collection.count_documents({}) + 1,
                    "title": request.form.get('title'),
                    "content": request.form.get('question'),
                    "account": session['username'],
                    "replies": []
                }
                recruiter_post_collection.insert_one(new_question)
            if 'form-type' in request.form:
                question_id = int(request.form.get('question_id', -1))
                reply_content = request.form.get('replyContent')
                question = recruiter_post_collection.find_one({'id': question_id})

                if question:
                    recruiter_post_collection.update_one(
                        {'id': question_id},
                        {'$push': {'replies': {"content": reply_content, "reply_account": session['username']}}}
                    )
            if 'candidates' in request.form:
                print('cand')
                return render_template(url_for('dash'))
            return redirect(url_for('posts'))
        data = list(recruiter_post_collection.find({}))
        return render_template('posts.html', questions=data, author_name=session.get('username'))
    return redirect('signup')


@app.route("/internship", methods=['GET', 'POST'])
def internship():
    api_url = 'https://zobjobs.com/api/jobs'
    response = requests.get(api_url)
    response.raise_for_status()
    jobs = response.json()
    with open('data/jobs.json', encoding='utf-8') as f:
        data = json.load(f)
    if request.method == 'POST':
        if 'search' in request.form:
            target = request.form.get('search')
            print(request.form.get('search'))
            jobloc = []
            for d in data['jobs']:
                if target.lower() in d['location'].lower():
                    jobloc.append(d)
            return render_template('internship.html', jobs=jobloc)
        if 'skills' in request.form or 'interests' in request.form:
            jobskill = []
            skill = request.form.get('skills')
            interest = request.form.get('interests')
            for d in data['jobs']:
                if skill != 'none' or skill != 'None':
                    if skill in d['category']:
                        jobskill.append(d)
                if interest != 'none' or interest != 'None':
                    if interest in d['title']:
                        jobskill.append(d)
            return render_template('internship.html', jobs=jobskill)
    return render_template('internship.html', jobs=jobs['jobs'])


@app.route('/find-candidates', methods=['GET', 'POST'])
def dash():
    if request.method == 'POST':
        print('kou4')
        post_id = request.form.get('post_id')
        required_skills, matching_profiles = set(), []
        data = recruiter_post_collection.find({})
        required_skills = {skill.strip().lower() for skill in data[int(post_id) - 1]['content'].split(',')}
        print(int(post_id))
        student_data = profile_collection.find({})
        for student_profile in student_data:
            student_skills = set(student_profile['skill_list'])
            common_skills = student_skills.intersection(required_skills)
            matching_percentage = (len(common_skills) / len(required_skills)) * 100
            if matching_percentage >= 20:
                matching_profiles.append(student_profile)
        if matching_profiles == []:
            flash('No candidates matched')
            return render_template('home.html', name=session.get('username'))
        print('Matching Profiles:', matching_profiles)
        return render_template('base.html', post=matching_profiles)
    return render_template('rec_dashboard.html', name=session.get('username'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if session:
        if request.method == 'POST':
            profile_data = {
                'name': request.form.get('Name'),
                'email': request.form.get('email'),
                'headline': request.form.get('headline'),
                'location': request.form.get('location'),
                'industry': request.form.get('industry'),
                'skills': request.form.get('skills'),
                'skill_list': [skill.strip() for skill in request.form.get('skills').split(',')],
                'experience': request.form.get('experience'),
                'education': request.form.get('education'),
                'account': session['username']
            }
            profile_collection.insert_one(profile_data)
            return render_template('final-prof.html', profile_data=profile_data)
        all_coll = profile_collection.find({})
        for i in all_coll:
            if i['account'] == session['username']:
                return render_template('final-prof.html', profile_data=i)
        return render_template('profile.html')
    return render_template(url_for('signup'))


@app.route('/java', methods=['GET', 'POST'])
def java():
    if 'username' in session:
        if request.method == 'POST':
            if 'title' in request.form:
                new_question = {
                    "id": java_collection.count_documents({}) + 1,
                    "title": request.form.get('title'),
                    "content": request.form.get('question'),
                    "account": session['username'],
                    "replies": []
                }
                java_collection.insert_one(new_question)
            if 'form-type' in request.form:
                question_id = int(request.form.get('question_id', -1))
                reply_content = request.form.get('replyContent')
                question = java_collection.find_one({'id': question_id})

                if question:
                    java_collection.update_one(
                        {'id': question_id},
                        {'$push': {'replies': {"content": reply_content, "reply_account": session['username']}}}
                    )
            return redirect(url_for('java'))
        author_name = session.get('username')
        data = list(java_collection.find({}))
        return render_template('java.html', questions=data, author_name=author_name)
    return redirect('signup')


@app.route('/machine-learning', methods=['GET', 'POST'])
def machine_learning():
    if 'username' in session:

        if request.method == 'POST':
            if 'title' in request.form:
                new_question = {
                    "id": machine_learning_collection.count_documents({}) + 1,
                    "title": request.form.get('title'),
                    "content": request.form.get('question'),
                    "account": session['username'],
                    "replies": []
                }
                machine_learning_collection.insert_one(new_question)
            if 'form-type' in request.form:
                question_id = int(request.form.get('question_id', -1))
                reply_content = request.form.get('replyContent')
                question = machine_learning_collection.find_one({'id': question_id})

                if question:
                    machine_learning_collection.update_one(
                        {'id': question_id},
                        {'$push': {'replies': {"content": reply_content, "reply_account": session['username']}}}
                    )
            return redirect(url_for('machine_learning'))
        author_name = session.get('username')
        data = list(machine_learning_collection.find({}))
        return render_template('ml.html', questions=data, author_name=author_name)
    return redirect('signup')


@app.route('/webdev', methods=['GET', 'POST'])
def webdev():
    if 'username' in session:
        if request.method == 'POST':

            if 'title' in request.form:
                new_question = {
                    "id": webdev_collection.count_documents({}) + 1,
                    "title": request.form.get('title'),
                    "content": request.form.get('question'),
                    "account": session['username'],
                    "replies": []
                }
                webdev_collection.insert_one(new_question)

            if 'form-type' in request.form:
                question_id = int(request.form.get('question_id', -1))
                reply_content = request.form.get('replyContent')
                question = webdev_collection.find_one({'id': question_id})

                if question:
                    webdev_collection.update_one(
                        {'id': question_id},
                        {'$push': {'replies': {"content": reply_content, "reply_account": session['username']}}}
                    )
            return redirect(url_for('webdev'))
        author_name = session.get('username')
        data = list(webdev_collection.find({}))
        return render_template('webdev.html', questions=data, author_name=author_name)
    return redirect('signup')


@app.route('/python', methods=['GET', 'POST'])
def python():
    if 'username' in session:
        if request.method == 'POST':
            if 'title' in request.form:
                new_question = {
                    "id": python_collection.count_documents({}) + 1,
                    "title": request.form.get('title'),
                    "content": request.form.get('question'),
                    "account": session['username'],
                    "replies": []
                }
                python_collection.insert_one(new_question)
            if 'form-type' in request.form:
                question_id = int(request.form.get('question_id', -1))
                reply_content = request.form.get('replyContent')
                question = python_collection.find_one({'id': question_id})
                if question:
                    python_collection.update_one(
                        {'id': question_id},
                        {'$push': {'replies': {"content": reply_content, "reply_account": session['username']}}}
                    )
            return redirect(url_for('python'))
        author_name = session.get('username')
        data = list(python_collection.find({}))
        for i in data:
            print(i)
        return render_template('python.html', questions=data, author_name=author_name)
    return redirect('signup')


@app.route('/cybersecurity', methods=['GET', 'POST'])
def cybersecurity():
    if 'username' in session:
        # with open('data/cybersecurity.json') as f:
        #     data = json.load(f)
        data = cybersecurity_collection.find({})

        if request.method == 'POST':

            if 'title' in request.form:
                new_question = {
                    "id": cybersecurity_collection.count_documents({}) + 1,
                    "title": request.form.get('title'),
                    "content": request.form.get('question'),
                    "account": session['username'],
                    "replies": []
                }
                cybersecurity_collection.insert_one(new_question)

            if 'form-type' in request.form:
                question_id = int(request.form.get('question_id', -1))
                reply_content = request.form.get('replyContent')
                question = cybersecurity_collection.find_one({'id': question_id})

                if question:
                    cybersecurity_collection.update_one(
                        {'id': question_id},
                        {'$push': {'replies': {"content": reply_content, "reply_account": session['username']}}}
                    )

            # with open('data/cybersecurity.json', 'w') as f:
            #     json.dump(data, f, indent=2)
            # cybersecurity_collection.insert_one(data)
            # cybersecurity_collection.insert_one(new_question)

            return redirect(url_for('cybersecurity'))
        author_name = session.get('username')

        return render_template('cybersecurity.html', questions=data, author_name=author_name)
    return redirect('signup')


@app.route("/community", methods=['GET', 'POST'])
def community():
    if request.method == 'POST':
        if 'join-java' in request.form:
            data = community_collection.find({})
            if community_collection.count_documents({}) != 0:
                for d in data:
                    if d['username'] == session['username']:
                        d['joined'].append('java')
                        break
            community_collection.insert_one({'username': session['username'], 'joined': ['java']})
            flash('Joined the Java community')
            return redirect('java')

        elif 'join-webdev' in request.form:
            data = community_collection.find({})
            if community_collection.count_documents({}) != 0:
                for d in data:
                    if d['username'] == session['username']:
                        d['joined'].append('webdev')
                        break
            else:
                community_collection.insert_one({'username': session['username'], 'joined': ['webdev']})
            flash('Joined the Web development community')
            return redirect('webdev')

        elif 'join-python' in request.form:
            data = community_collection.find({})
            if community_collection.count_documents({}) != 0:
                for d in data:
                    if d['username'] == session['username']:
                        d['joined'].append('python')
                        break
            else:
                community_collection.insert_one({'username': session['username'], 'joined': ['python']})
            flash('Joined the Python community')
            return redirect('python')

        elif 'join-machine-learning' in request.form:
            data = community_collection.find({})
            if community_collection.count_documents({}) != 0:
                for d in data:
                    if d['username'] == session['username']:
                        d['joined'].append('machine learning')
                        break
            else:
                community_collection.insert_one({'username': session['username'], 'joined': ['machine learning']})
            flash('Joined the Machine learning community')
            return redirect('machine_learning')

        elif 'join-cybersecurity' in request.form:
            data = community_collection.find({})
            if community_collection.count_documents({}) != 0:
                for d in data:
                    if d['username'] == session['username']:
                        d['joined'].append('cybersecurity')
                        break
            else:
                community_collection.insert_one({'username': session['username'], 'joined': ['cybersecurity']})
            flash('Joined the Cybersecurity community')
            return redirect('cybersecurity')

    return render_template('community.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        account_type = request.form.get('type')
        data = signup_collection.find({})
        for index, user in enumerate(data):
            if user['username'] == username and user['password'] == password:
                session['user_id'] = index
                session['username'] = user['username']
                session['type'] = user['type']
                flash('Login successful!', 'success')
                if account_type == 'recruiter':
                    return redirect(url_for('dash', name=session['username']))
                return redirect(url_for('index', name=username))
        flash('Login unsuccessful. Please check your username and password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        account_type = request.form.get('type')
        existing_user = signup_collection.find_one({'username': username})
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('signup'))
        if not (username and email and password):
            flash('Please fill out all fields', 'error')
            return redirect(url_for('signup'))
        signup_collection.insert_one({'username': username, 'email': email, 'password': password, 'type': account_type})
        flash('Account created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)
