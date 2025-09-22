# Vizify

## Overview
**Vizify** is a comprehensive Python package designed to automate the process of data visualization, analysis, and machine learning. It generates comprehensive PDF reports containing a wide variety of plots and visual summaries, provides an interactive Streamlit dashboard for live data exploration, and now includes **no-code machine learning capabilities** for predictive modeling.

Whether you're a data scientist, business analyst, or beginner, Vizify speeds up exploratory data analysis, enables predictive modeling, and makes your datasets visually insightful with minimal effort.

---

## ✨ Features

### 📊 **Data Visualization & Analysis**
- **Basic Statistics:** Summarizes key numerical insights and data quality metrics
- **Correlation Heatmap:** Displays relationships between numerical features
- **Distribution Plots:** Visualizes data distributions with histograms and KDE
- **Box Plots:** Highlights outliers and data spread
- **Scatter Plots:** Shows relationships between numerical variables with optional color coding
- **Violin Plots:** Combines box plots and density estimates
- **Word Cloud:** Extracts textual insights from categorical features
- **Outlier Detection:** Identifies extreme values using statistical methods
- **Stacked Bar Charts:** Compares categorical data distributions
- **Line Plots:** Represents trends over time with multiple series support
- **Pie Charts:** Displays categorical distributions with percentages
- **Time-Series Analysis:** Visualizes and interprets temporal trends in date/time features
- **Anomaly Detection:** Detects and visualizes unusual patterns or outliers in time-series data

### 🤖 **Machine Learning Capabilities (NEW)**
- **No-Code ML Training:** Train machine learning models without writing code
- **Multiple Algorithm Support:** Compare 5+ algorithms simultaneously
  - **Regression:** Linear Regression, Random Forest, Decision Trees, SVM, K-Nearest Neighbors
  - **Classification:** Logistic Regression, Random Forest, Decision Trees, SVM, K-Nearest Neighbors
- **Automated Preprocessing:** Handles missing values, categorical encoding, and feature scaling
- **Smart Problem Detection:** Automatically suggests regression vs classification based on target variable
- **Model Performance Comparison:** Visual charts comparing model accuracy/performance
- **Model Export:** Download trained models as `.pkl` files for production use
- **Prediction Visualization:** Scatter plots for regression, confusion matrices for classification
- **Usage Instructions:** Auto-generated Python code for using exported models

### 🚀 **AI-Powered Features**
- **AI-Powered Chart Insights:** Uses Gemini LLM to automatically interpret charts and provide natural-language explanations
- **Automated Report Generation:** Saves all visualizations in a structured PDF report with AI commentary
- **Smart Data Profiling:** AI-driven insights about data quality and patterns

### 📱 **Interactive Dashboard**
- **Real-time Data Exploration:** Dynamic Streamlit dashboard with live filtering
- **Global Data Slicers:** Filter entire dashboard by date ranges, categories, and numerical ranges
- **Drag-and-Drop Interface:** Build custom dashboards by adding/removing visualizations
- **Export Capabilities:** Download filtered data as CSV or entire dashboard as PDF
- **ML Model Training Interface:** Train and compare models directly in the dashboard

---

## 📦 Installation

Install Vizify using pip:

```bash
pip install vizify
```

---

## 🚀 Usage

### 1. Import the Package

```python
from vizify import Vizify
```

### 2. Generate a Basic Visualization Report

```python
from vizify import Vizify

# Initialize Vizify with a CSV file
viz = Vizify("your_data.csv")
viz.show_all_visualizations()
```

After execution, a file named `data_visualization_report.pdf` will be created in your working directory containing all the visualizations.

### 3. Generate a Visualization Report with AI Interpretation

```python
from vizify import Vizify

viz = Vizify("your_data.csv", api_key="YOUR_GEMINI_API_KEY")#Place your API KEY here
viz.show_all_visualizations()
```

### 4. Launch Interactive Dashboard (NEW)

Run Vizify as a script to access the interactive dashboard:

```bash
python -c "from vizify import run_dashboard; run_dashboard()"
```

Or use the command-line interface:

```python
if __name__ == "__main__":
    # This will prompt you to choose between PDF report or interactive dashboard
    from vizify import main
    main()
```

### 5. Machine Learning Training (NEW)
## 🧠 ML Model Training via Interactive Dashboard

Vizify’s dashboard makes machine learning effortless. Just follow these steps:

### 1️⃣ Upload Your CSV File
Use the file uploader in the sidebar to load your dataset.

### 2️⃣ Enable ML Model Training
From the sidebar, check the **"ML Model Training"** option to activate the training wizard.

### 3️⃣ Follow the Step-by-Step Wizard

- **Choose Problem Type:**  
  Select whether you're solving a **Regression** or **Classification** problem.

- **Select Features and Target Variable:**  
  Pick the input features and the column you want to predict.

- **Configure Preprocessing Options:**  
  Handle missing values, encode categorical variables, and scale features.

- **Select Algorithms to Compare:**  
  Choose from multiple models like Linear/Logistic Regression, Random Forest, Decision Trees, SVM, and KNN.

- **Train Models with One Click:**  
  Run training and view performance metrics instantly.

### 4️⃣ Download Trained Models
Export your best-performing model as a `.pkl` file for production use.

---

This flow turns Vizify into a no-code ML powerhouse—perfect for analysts, business users, and data scientists alike.

---

## ⚙️ Optional Usage

You can also use specific methods for targeted visualizations:

```python
viz.plot_correlation_heatmap()
viz.plot_time_series(column="date_column", value="sales")
viz.detect_anomalies(column="sales", method="iqr")
```

---

## 📚 Dependencies

Vizify requires the following Python libraries:

- [pandas](https://pypi.org/project/pandas/)
- [numpy](https://pypi.org/project/numpy/)
- [seaborn](https://pypi.org/project/seaborn/)
- [matplotlib](https://pypi.org/project/matplotlib/)
- [missingno](https://pypi.org/project/missingno/)
- [wordcloud](https://pypi.org/project/wordcloud/)
- [scikit-learn](https://pypi.org/project/scikit-learn/)
- ipywidgets
- streamlit
- plotly
- st_aggrid
- streamlit_plotly_events
- kaleido

These will be automatically installed when you install Vizify.

---

## 📈 Upcoming Features

- **Custom Theme Support:** Dark/light mode and aesthetic customizations.
- **Drill-Down Interactivity:** Clickable charts for deeper data exploration.
- **Hyperparameter tuning with grid search:** Adding the Hyperparameter into ML Models

---

## 🧑‍💻 Contribution

Contributions are welcome! To contribute:

1. Fork the repository  
2. Create a new branch (`git checkout -b feature-xyz`)  
3. Commit your changes  
4. Push to the branch  
5. Submit a pull request  

---

## 📄 License

Vizify is released under the [MIT License](LICENSE.txt).

---

## 📬 Contact

- **Author:** Arun M  
- **Email:** arunpappulli@gmail.com  
- **GitHub:** [arun6832](https://github.com/arun6832)

---

<a href="https://pepy.tech/projects/vizify"><img src="https://static.pepy.tech/badge/vizify" alt="PyPI Downloads"></a>

Thank you for using **Vizify**! 🚀
