from flask import Flask, render_template, request, redirect, url_for
import subprocess
import os

app = Flask(__name__)

# プログラムの状態を追跡する変数
is_running = False
process = None

@app.route('/')
def index():
    return render_template('index.html', is_running=is_running)

@app.route('/toggle_script', methods=['POST'])
def toggle_script():
    global is_running, process
    if is_running:
        # プログラムが実行中の場合、停止する
        if process:
            process.terminate()
        is_running = False
    else:
        # プログラムが停止中の場合、開始する
        process = subprocess.Popen(["python", "detect_face.py"])
        is_running = True
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host = "0.0.0.0", debug=True)