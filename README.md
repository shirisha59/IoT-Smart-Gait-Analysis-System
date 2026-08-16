# IoT Smart Gait Analysis System

An IoT-based smart gait analysis system designed to analyze walking patterns and assist in detecting gait abnormalities associated with Parkinson's disease. The system collects gait-related data, processes the data using machine learning, and provides patient-specific analysis through a web-based dashboard.

## Project Overview

Gait abnormalities are one of the important motor symptoms associated with Parkinson's disease. Early identification of abnormal walking patterns can support further clinical evaluation.

This project combines **IoT, machine learning, Python, Flask, and web technologies** to develop a system that analyzes gait data and classifies walking patterns as normal or Parkinsonian.

## Key Features

* Collect and process gait-related patient data
* Analyze normal and Parkinsonian walking patterns
* Machine learning-based gait classification
* Patient data management
* Patient report generation
* Web-based dashboard
* User authentication with login and signup
* Visualization of gait analysis results
* Patient history tracking
* Statistical analysis of gait data

## System Workflow

```text
Gait Data Collection
        ↓
Data Preprocessing
        ↓
Feature Extraction
        ↓
Machine Learning Model
        ↓
Gait Classification
        ↓
Flask Backend
        ↓
Web Dashboard
        ↓
Patient Report & Analysis
```

## Technologies Used

### Programming Languages

* Python
* HTML
* CSS
* JavaScript

### Backend

* Flask
* SQLite

### Machine Learning

* Scikit-learn
* Machine Learning Classification Model
* Feature Scaling

### Frontend

* HTML
* CSS
* JavaScript
* Flask Templates

### Data Processing

* Pandas
* NumPy

### Development Tools

* VS Code
* Git
* GitHub

## Project Structure

```text
IoT-Smart-Gait-Analysis-System/
│
├── collect_patient_data.py
├── normal_walk.csv
├── parkinson_walk.csv
├── norml_test.txt
├── pk_test.txt
├── patient_data.csv
├── database.db
│
└── project/
    ├── app.py
    ├── database.db
    ├── patient_data.csv
    ├── patient_report.txt
    ├── parkinson_model.pkl
    ├── scaler.pkl
    ├── requirements.txt
    │
    └── templates/
        ├── dashboard.html
        ├── history.html
        ├── login.html
        ├── signup.html
        └── stats.html
```

## Machine Learning Model

The system uses gait-related data to distinguish between normal walking patterns and Parkinsonian walking patterns.

The machine learning pipeline consists of:

1. Data collection
2. Data preprocessing
3. Feature extraction
4. Feature scaling
5. Model training
6. Model evaluation
7. Prediction on new patient data

The trained model and scaler are stored as:

```text
parkinson_model.pkl
scaler.pkl
```

## Web Application

The Flask application provides a web interface for interacting with the gait analysis system.

### Main Modules

**Login and Signup**

Allows users to securely access the application.

**Dashboard**

Provides an overview of the patient's gait analysis.

**Patient Data**

Stores and manages patient-related information.

**Gait Analysis**

Processes gait data and generates a prediction.

**History**

Displays previous patient analysis results.

**Statistics**

Provides statistical information and visual analysis.

**Patient Report**

Generates a report based on the gait analysis results.

## Installation

Clone the repository:

```bash
git clone https://github.com/shirisha59/IoT-Smart-Gait-Analysis-System.git
```

Navigate to the project:

```bash
cd IoT-Smart-Gait-Analysis-System/project
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Run the Flask application:

```bash
python app.py
```

The application will start on the local Flask development server.

Open the URL displayed in the terminal in your web browser.

## Dataset

The project contains gait data representing:

* Normal walking patterns
* Parkinsonian walking patterns

The data is processed to extract useful gait-related characteristics for machine learning-based classification.

> Note: Any patient-related data included in this repository should be anonymized and used only for research or demonstration purposes.

## Results

The system provides:

* Gait classification results
* Patient-specific analysis
* Historical analysis
* Statistical information
* Generated patient reports
* Web-based visualization

## Applications

* Gait pattern analysis
* Parkinson's disease research
* Assistive healthcare systems
* Remote patient monitoring
* Academic and research applications
* IoT-based healthcare solutions

## Future Enhancements

* Integration with real-time wearable sensors
* Real-time gait monitoring
* Mobile application support
* Cloud-based patient monitoring
* Improved machine learning models
* Real-time alerts for abnormal gait patterns
* Integration with additional gait parameters
* Advanced visualization and analytics
* Deployment on an IoT edge device

## Disclaimer

This project is intended for **educational and research purposes**. The predictions generated by the system should not be considered a medical diagnosis. Clinical decisions should always be made by qualified healthcare professionals.

## Author

**Shirisha Mangenapally**

GitHub: [@shirisha59](https://github.com/shirisha59)
