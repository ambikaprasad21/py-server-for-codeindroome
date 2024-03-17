

import logging
import matplotlib


matplotlib.use('Agg')

from flask import Flask, jsonify, render_template, send_file, request
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
from zipfile import ZipFile  
from flask_cors import CORS  

app = Flask(__name__)
CORS(app)  

def generate_colored_chart(df, filename):
    plt.figure(figsize=(10, 6))
    colors = ['red', 'green', 'blue', 'orange', 'purple']

    for idx, column in enumerate(df.select_dtypes(include=['int', 'float']).columns):
        plt.plot(df.index, df[column], label=column, color=colors[idx % len(colors)])

    plt.xlabel('Data Points')
    plt.ylabel(', '.join(df.select_dtypes(include=['int', 'float']).columns))
    plt.title(f'Plot for all Integer value columns in {filename} file')
    plt.legend()

    image_stream =  BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    plt.close()

    # Describe Chart
    plt.figure(figsize=(10, 6))
    sns.heatmap(df.describe().transpose(), annot=True, cmap='viridis', fmt='.2f')
    plt.title('Summary Statistics of Data')
    plt.xlabel('Statistical Measures')
    plt.ylabel('Columns')

    describe_chart_stream = BytesIO()
    plt.savefig(describe_chart_stream, format='png')
    describe_chart_stream.seek(0)
    plt.close()

    return image_stream, describe_chart_stream

def generate_two_column_chart(df, column1, column2):
    plt.figure(figsize=(10, 6))
    plt.plot(df[column1], df[column2], 'o', color='green')

    plt.xlabel(column1)
    plt.ylabel(column2)
    plt.title(f'Plot between {column1} and {column2}')

    image_stream =  BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    plt.close()

    return image_stream


# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    try:

        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return "Unsupported file format"
        # df = pd.read_csv(file)

        # int_columns = df.select_dtypes(include='int')

        image_stream, describe_chart_stream = generate_colored_chart(df, file.filename)

        # return send_file(image_stream, mimetype='image/png'), send_file(describe_chart_stream, mimetype='image/png')

        zip_stream = BytesIO()
        with ZipFile(zip_stream, 'w') as zipf:
            zipf.writestr('colored_chart.png', image_stream.read())
            zipf.writestr('describe_chart.png', describe_chart_stream.read())

        zip_stream.seek(0)
        return send_file(zip_stream, mimetype='application/zip', as_attachment=True, download_name='charts.zip')

    except Exception as e:
        return jsonify({'error': f"Error processing CSV file: {str(e)}"})

@app.route('/generate_two_column_chart', methods=['POST'])
def generate_two_column_chart_route():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"
    
    if 'column1' in request.form and 'column2' in request.form:
        
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.filename.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                return "Unsupported file format"
    
            logging.info(f"Loaded dataframe:\n{df.head()}")
            
            column1 = request.form['column1']
            column2 = request.form['column2']
            # df = pd.read_csv(request.files['file'])
            image_stream = generate_two_column_chart(df, column1, column2)
 
            return send_file(image_stream, mimetype='image/png')

        except Exception as e:
            return jsonify({'error': f"Error generating two-column chart: {str(e)}"})

        except Exception as e:
            return f"Error processing CSV file: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
