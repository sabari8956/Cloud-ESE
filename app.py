from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import pandas as pd
import requests
from io import BytesIO
import boto3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# S3 Configuration
S3_BUCKET = '2340154-cloud26'
S3_REGION = 'us-east-1'
STUDENT_DOCS_PREFIX = 'student_docs/'

# Initialize S3 client
s3_client = boto3.client('s3', region_name='us-east-1')

def fetch_excel_from_s3(url):
    """Fetch Excel file from S3 and return pandas DataFrame"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            excel_data = BytesIO(response.content)
            df = pd.read_excel(excel_data, engine='openpyxl')
            return df, None
        elif response.status_code == 403:
            return None, "Access Denied"
        else:
            return None, "Access Denied"
    except Exception as e:
        return None, "Access Denied"

@app.route('/')
def home():
    return render_template('home.html')

def get_next_attendance_number():
    """Get the next available attendance number by checking existing files in S3"""
    try:
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET,
            Prefix=STUDENT_DOCS_PREFIX + 'attendence-'
        )

        if 'Contents' not in response:
            return 1

        # Extract numbers from existing attendence files
        numbers = []
        for obj in response['Contents']:
            filename = obj['Key'].split('/')[-1]
            if filename.startswith('attendence-') and filename.endswith('.csv'):
                try:
                    num = int(filename.replace('attendence-', '').replace('.csv', ''))
                    numbers.append(num)
                except ValueError:
                    continue

        return max(numbers) + 1 if numbers else 1
    except Exception as e:
        print(f"Error getting attendance number: {e}")
        return 1

@app.route('/student_docs')
def student_docs():
    url = "https://2340154-cloud26.s3.us-east-1.amazonaws.com/student_docs/student.xlsx"
    df, error = fetch_excel_from_s3(url)

    if error:
        return render_template('student_docs.html', error=error)

    # Convert DataFrame to HTML table
    table_html = df.to_html(classes='data-table', index=False, border=0)
    return render_template('student_docs.html', table_html=table_html, columns=df.columns.tolist())

@app.route('/upload_attendance', methods=['POST'])
def upload_attendance():
    """Handle CSV file upload for student attendance"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'Only CSV files are allowed'}), 400

        # Get next attendance number
        attendance_num = get_next_attendance_number()
        new_filename = f'attendence-{attendance_num:02d}.csv'

        # Upload to S3
        s3_key = STUDENT_DOCS_PREFIX + new_filename
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            s3_key,
            ExtraArgs={'ContentType': 'text/csv'}
        )

        s3_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"

        return jsonify({
            'success': True,
            'message': f'File uploaded successfully as {new_filename}',
            'filename': new_filename,
            'url': s3_url
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/staff_docs')
def staff_docs():
    url = "https://2340154-cloud26.s3.us-east-1.amazonaws.com/staff_docs/staff.xlsx"
    df, error = fetch_excel_from_s3(url)

    if error:
        return render_template('staff_docs.html', error=error)

    # Convert DataFrame to HTML table
    table_html = df.to_html(classes='data-table', index=False, border=0)
    return render_template('staff_docs.html', table_html=table_html, columns=df.columns.tolist())

if __name__ == '__main__':
    app.run(debug=True)
