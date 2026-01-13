from flask import Flask, render_template
import pandas as pd
import requests
from io import BytesIO

app = Flask(__name__)

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

@app.route('/student_docs')
def student_docs():
    url = "https://2340154-cloud26.s3.us-east-1.amazonaws.com/student_docs/student.xlsx"
    df, error = fetch_excel_from_s3(url)

    if error:
        return render_template('student_docs.html', error=error)

    # Convert DataFrame to HTML table
    table_html = df.to_html(classes='data-table', index=False, border=0)
    return render_template('student_docs.html', table_html=table_html, columns=df.columns.tolist())

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
