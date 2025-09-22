# 🚀 Keeya - AI-Powered Python Code Generation

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/keeya.svg)](https://badge.fury.io/py/keeya)

Transform natural language into executable Python code for data analysis, cleaning, and machine learning.

## ✨ Features

- 🤖 **Natural Language to Code**: Generate Python code from plain English
- 🧹 **Smart Data Cleaning**: Automatically handle missing values, duplicates, and data types
- 📊 **Instant Analysis**: Get comprehensive statistics and insights
- 📈 **Auto Visualizations**: Generate relevant plots based on your data
- 🎯 **ML Pipeline Generation**: Build complete machine learning workflows
- 🔒 **Safe & Secure**: Review code before execution, powered by Google Gemini

## 🚀 Quick Start

### Installation
```bash
pip install keeya
```

### Setup (One-time)
```python
import keeya
keeya.setup()  # Enter your free Gemini API key
```

### Basic Usage
```python
import pandas as pd
import keeya

# Load your data
df = pd.read_csv('data.csv')

# Generate code for any task
code = keeya.generate("create a function to calculate fibonacci numbers")

# Clean your data
cleaned_code = keeya.clean(df)

# Analyze your data  
analysis = keeya.analyze(df)

# Create visualizations
viz_code = keeya.visualize(df)

# Build ML pipeline
ml_code = keeya.train(df, target='target_column')
```

## 🎯 Why Keeya?

- **Simple**: One consistent API across all functions
- **Smart**: Context-aware code generation based on your actual data
- **Safe**: Always returns code for you to review and execute
- **Free**: Powered by Google Gemini's free tier
- **Fast**: Get results in seconds, not hours

## 🔑 Getting Your API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key and paste it when running `keeya.setup()`

## 📖 Documentation

Run `keeya.help()` for detailed usage information and examples.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

Keeya generates code using AI. Always review generated code before executing in production environments.