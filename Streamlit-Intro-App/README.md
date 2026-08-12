# Streamlit Intro App

A simple **data dashboard** built with **Streamlit** for CSV analysis and visualization — perfect for learning Streamlit basics.

---

## 📋 Features

- 📁 **CSV Upload** — Drag-and-drop file upload
- 📊 **Data Preview** — View first rows of uploaded data
- 📈 **Summary Statistics** — Automatic descriptive statistics
- 🔍 **Column Filtering** — Select specific columns to display
- 📉 **Chart Generation** — Interactive line charts

---

## 🚀 Getting Started

```bash
cd Streamlit-Intro-App
pip install streamlit pandas
streamlit run main.py
```

---

## 📖 Logic Flow

1. **Upload** — User uploads a CSV file via drag-and-drop
2. **Preview** — First N rows displayed as a table
3. **Statistics** — `df.describe()` shows summary stats
4. **Filter** — User selects columns to focus on
5. **Visualize** — Line chart generated from selected data

---

## 📦 Dependencies
`streamlit`, `pandas`

---

## 📝 License
Educational project — use freely for learning and reference.
