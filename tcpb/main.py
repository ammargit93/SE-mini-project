import json
from flask import *
import requests

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
        with open('data/qna.json') as f:
            data = json.load(f)
        if request.method == 'POST':
            if 'title' in request.form:
                new_question = {
                    "id": len(data["questions"]) + 1,
                    "title": request.form.get('title'),
                    "content": request.form.get('question'),
                    "account": session['username'],
                    "likes": 0,
                    "replies": []
                }
                data["questions"].append(new_question)
            if 'form-type' in request.form:
                question_id = int(request.form.get('question_id', -1))
                reply_content = request.form.get('replyContent')
                if question_id != -1:
                    question = next((q for q in data["questions"] if q["id"] == question_id), None)
                    if question:
                        question["replies"].append({"content": reply_content})
            with open('data/qna.json', 'w') as f:
                json.dump(data, f, indent=2)
            return redirect(url_for('qna'))
        author_name = session.get('username')
        return render_template('qna.html', questions=data.get("questions", []), author_name=author_name)
    return redirect('signup')


# recruiter posts
@app.route("/posts", methods=['GET', 'POST'])
def posts():
    if 'username' in session:
        with open('data/recruiter_posts.json') as f:
            data = json.load(f)
        if request.method == 'POST':
            if 'title' in request.form:
                new_question = {
                    "id": len(data["posts"]) + 1,
                    "title": request.form.get('title'),
                    "content": request.form.get('question'),
                    "account": session['username']
                }
                data["posts"].append(new_question)
            if 'form-type' in request.form:
                question_id = int(request.form.get('question_id', -1))
                reply_content = request.form.get('replyContent')
                if question_id != -1:
                    question = next((q for q in data["posts"] if q["id"] == question_id), None)
                    if question:
                        question["replies"].append({"content": reply_content})
            with open('data/recruiter_posts.json', 'w') as f:
                json.dump(data, f, indent=2)
            return redirect(url_for('posts'))
        author_name = session.get('username')
        return render_template('posts.html', questions=data.get("posts", []), author_name=author_name)
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
        rlist, slist = [], []
        with open('data/rec-profile.json') as f:
            r = json.load(f)
        with open('data/profile.json') as f:
            s = json.load(f)
        for r in r['recruiter-profile']:
            if r['name'] == session['username']:
                rlist = r.get('req_list')
                break

        flist = []
        with open('data/applicant.json') as f:
            d = json.load(f)
        for stud in s['student-profile']:
            slist = stud['skill_list']
            for skill in slist:
                if skill in rlist:
                    flist.append(skill)

            if (len(flist) / len(rlist)) * 100 > 70:
                print("match found")

                d['applicant'].append({"rec-account": session['username'],
                                       "app_skills": stud['skills'],
                                       "app_name": stud['name'],
                                       "app_email": stud['email']})

        return redirect(url_for('index'))
    return render_template('rec_dashboard.html', name=session['username'])


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    with open('data/profile.json', 'r') as f:
        info = json.load(f)
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

        info['student-profile'].append(profile_data)
        with open('data/profile.json', 'w') as f:
            json.dump(info, f, indent=2)
        return render_template('final-prof.html', profile_data=profile_data)
    for i in info['student-profile']:
        if i['account'] == session['username']:
            return render_template('final-prof.html', profile_data=i)
    return render_template('profile.html')


@app.route('/java', methods=['GET', 'POST'])
def java():
    if 'username' in session:
        with open('data/java.json') as f:
            data = json.load(f)
        if request.method == 'POST':
            if 'title' in request.form:
                new_question = {
                    "id": len(data["java_forum"]) + 1,
                    "title": request.form.get('title'),
                    "content": request.form.get('question'),
                    "account": session['username'],
                    "replies": []
                }
                data["java_forum"].append(new_question)
            if 'form-type' in request.form:
                question_id = int(request.form.get('question_id', -1))
                reply_content = request.form.get('replyContent')
                if question_id != -1:
                    question = next((q for q in data["java_forum"] if q["id"] == question_id), None)
                    if question:
                        question["replies"].append({"content": reply_content})
            with open('data/java.json', 'w') as f:
                json.dump(data, f, indent=2)
            return redirect(url_for('java'))
        author_name = session.get('username')
        return render_template('java.html', questions=data.get("java_forum", []), author_name=author_name)
    return redirect('signup')


@app.route('/webdev', methods=['GET', 'POST'])
def webdev():
    if 'username' in session:
        with open('data/webdev.json') as f:
            data = json.load(f)
        if request.method == 'POST':
            if 'title' in request.form:
                new_question = {
                    "id": len(data["web_forum"]) + 1,
                    "title": request.form.get('title'),
                    "content": request.form.get('question'),
                    "account": session['username'],
                    "replies": []
                }
                data["web_forum"].append(new_question)
            if 'form-type' in request.form:
                question_id = int(request.form.get('question_id', -1))
                reply_content = request.form.get('replyContent')
                if question_id != -1:
                    question = next((q for q in data["web_forum"] if q["id"] == question_id), None)
                    if question:
                        question["replies"].append({"content": reply_content})
            with open('data/webdev.json', 'w') as f:
                json.dump(data, f, indent=2)
            return redirect(url_for('webdev'))
        author_name = session.get('username')
        return render_template('webdev.html', questions=data.get("web_forum", []), author_name=author_name)
    return redirect('signup')


@app.route('/python', methods=['GET', 'POST'])
def python():
    if 'username' in session:
        with open('data/python.json') as f:
            data = json.load(f)
        if request.method == 'POST':
            if 'title' in request.form:
                new_question = {
                    "id": len(data["python_forum"]) + 1,
                    "title": request.form.get('title'),
                    "content": request.form.get('question'),
                    "account": session['username'],
                    "replies": []
                }
                data["python_forum"].append(new_question)
            if 'form-type' in request.form:
                question_id = int(request.form.get('question_id', -1))
                reply_content = request.form.get('replyContent')
                if question_id != -1:
                    question = next((q for q in data["python_forum"] if q["id"] == question_id), None)
                    if question:
                        question["replies"].append({"content": reply_content})
            with open('data/python.json', 'w') as f:
                json.dump(data, f, indent=2)
            return redirect(url_for('python'))
        author_name = session.get('username')
        return render_template('python.html', questions=data.get("python_forum", []), author_name=author_name)
    return redirect('signup')


@app.route('/cybersecurity', methods=['GET', 'POST'])
def cybersecurity():
    if 'username' in session:
        with open('data/cybersecurity.json') as f:
            data = json.load(f)
        if request.method == 'POST':
            if 'title' in request.form:
                new_question = {
                    "id": len(data["cybersecurity_forum"]) + 1,
                    "title": request.form.get('title'),
                    "content": request.form.get('question'),
                    "account": session['username'],
                    "replies": []
                }
                data["cybersecurity_forum"].append(new_question)
            if 'form-type' in request.form:
                question_id = int(request.form.get('question_id', -1))
                reply_content = request.form.get('replyContent')
                if question_id != -1:
                    question = next((q for q in data["cybersecurity_forum"] if q["id"] == question_id), None)
                    if question:
                        question["replies"].append({"content": reply_content})
            with open('data/cybersecurity.json', 'w') as f:
                json.dump(data, f, indent=2)
            return redirect(url_for('cybersecurity'))
        author_name = session.get('username')
        return render_template('cybersecurity.html', questions=data.get("cybersecurity_forum", []),
                               author_name=author_name)
    return redirect('signup')


@app.route("/community", methods=['GET', 'POST'])
def community():
    if request.method == 'POST':
        if 'join-java' in request.form:
            with open('data/community.json') as f:
                data = json.load(f)
            if len(data['community']) != 0:
                for d in data['community']:
                    if d['username'] == session['username']:
                        d['joined'].append('java')
                        break
            data['community'].append({'username': session['username'], 'joined': ['java']})
            with open('data/community.json', 'w') as f:
                json.dump(data, f, indent=2)
            flash('Joined the Java community')
            return redirect('java')

        elif 'join-webdev' in request.form:
            with open('data/community.json') as f:
                data = json.load(f)
            if len(data['community']) != 0:
                for d in data['community']:
                    if d['username'] == session['username']:
                        d['joined'].append('webdev')
                        break
            else:
                data['community'].append({'username': session['username'], 'joined': ['webdev']})
            with open('data/community.json', 'w') as f:
                json.dump(data, f, indent=2)
            flash('Joined the Web development community')
            return redirect('webdev')

        elif 'join-python' in request.form:
            with open('data/community.json') as f:
                data = json.load(f)
            if len(data['community']) != 0:
                for d in data['community']:
                    if d['username'] == session['username']:
                        d['joined'].append('python')
                        break
            else:
                data['community'].append({'username': session['username'], 'joined': ['python']})
            with open('data/community.json', 'w') as f:
                json.dump(data, f, indent=2)
            flash('Joined the Python community')
            return redirect('python')

        elif 'join-machine-learning' in request.form:
            with open('data/community.json') as f:
                data = json.load(f)
            if len(data['community']) != 0:
                for d in data['community']:
                    if d['username'] == session['username']:
                        d['joined'].append('machine learning')
                        break
            else:
                data['community'].append({'username': session['username'], 'joined': ['machine learning']})
            with open('data/community.json', 'w') as f:
                json.dump(data, f, indent=2)
            flash('Joined the Machine learning community')
            return redirect('machine_learning')

        elif 'join-cybersecurity' in request.form:
            with open('data/community.json') as f:
                data = json.load(f)
            if len(data['community']) != 0:
                for d in data['community']:
                    if d['username'] == session['username']:
                        d['joined'].append('cybersecurity')
                        break
            else:
                data['community'].append({'username': session['username'], 'joined': ['cybersecurity']})
            with open('data/community.json', 'w') as f:
                json.dump(data, f, indent=2)
            flash('Joined the Cybersecurity community')
            return redirect('cybersecurity')

    return render_template('community.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        account_type = request.form.get('type')
        with open('reg.json', 'r') as f:
            data = json.load(f)
        for index, user in enumerate(data['reg_info']):
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
        with open('reg.json') as f:
            data = json.load(f)
        if not (username and email and password):
            flash('Please fill out all fields', 'error')
            return redirect(url_for('signup'))
        data['reg_info'].append({'username': username, 'email': email, 'password': password, 'type': account_type})
        with open('reg.json', 'w') as f:
            json.dump(data, f, indent=2)
        flash('Account created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('signup.html')




if __name__ == '__main__':
    app.run(debug=True)
