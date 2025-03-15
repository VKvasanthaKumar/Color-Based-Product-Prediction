from flask import Flask, render_template, request, redirect, jsonify
import pandas as pd
import os
import Color_prediction

app = Flask(__name__)

data_file = "sorted_products.csv"
image_folder = "sorted_products"

# Load data
def load_data():
    if os.path.exists(data_file):
        return pd.read_csv(data_file)
    return pd.DataFrame(columns=["Timestamp", "Color", "Filename"])

@app.route('/')
def index():
    df = load_data()
    color_counts = df["Color"].value_counts().to_dict()
    colors = sorted(df["Color"].unique())
    return render_template("index_color.html", color_counts=color_counts, colors=colors, products=df.to_dict(orient='records'))

@app.route('/search', methods=['GET'])
def search():
    color = request.args.get('color')
    df = load_data()
    if color and color != "All":
        df = df[df["Color"] == color]
    return render_template("index_color.html", color_counts=df["Color"].value_counts().to_dict(), colors=sorted(df["Color"].unique()), products=df.to_dict(orient='records'))

@app.route('/start', methods=['POST'])
def start():
    Color_prediction.action()
    return redirect('/')

@app.route('/stop', methods=['POST'])
def stop():
    return redirect('/')

@app.route('/delete', methods=['POST'])
def delete():
    filename = request.form.get('filename')
    if not filename:
        return "No filename provided", 400

    # Delete image file from folder
    if os.path.exists(os.path.join(image_folder, filename)):
        os.remove(os.path.join(image_folder, filename))

    # Update the CSV file
    df = load_data()
    df = df[df['Filename'] != filename]
    df.to_csv(data_file, index=False)

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
