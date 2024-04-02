from flask import Flask, render_template
from flask_cors import CORS
from bokeh.embed import server_document


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about-us')
def about_us():
    return render_template('about-us.html')

@app.route('/info')
def info():
    return render_template('intro.html')

@app.route('/comparison')
def comp():
    return render_template('complexityComp.html')

@app.route('/jarvis-march')
def jarvis_march():
    return render_template('jarvisalgo.html')

@app.route('/jm_runtime')
def jm_runtime():
    return render_template('jm_runtime.html')

@app.route('/jm_epilogue')
def jm_epilogue():
    return render_template('jm_epilogue.html')

@app.route('/jarvis_march_visualisation')
def jarvis_march_visualisation():
    while True:
        bokeh_script = server_document('http://localhost:5006/jm')
        return render_template('jarvis_march_visualisation.html', script1=bokeh_script)

@app.route('/kirkpatrick_seidel')
def kirkpatrick_seidel():
    return render_template('kpsalgo.html')

@app.route('/kps_runtime')
def kps_runtime():
    return render_template('kps_runtime.html')

@app.route('/kps_epilogue')
def kps_epilogue():
    return render_template('kps_epilogue.html')

@app.route('/kps_visualisation')
def kps_visualisation():
    while True:
        bokeh_script=server_document('http://localhost:5006/kps')
        return render_template('kps.html', script1=bokeh_script)

if __name__ == '__main__':
    app.run(debug=True)