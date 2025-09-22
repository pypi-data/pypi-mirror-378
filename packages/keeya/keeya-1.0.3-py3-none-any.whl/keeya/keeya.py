"""
Keeya - Simple AI-Powered Data Analysis Tool
Simple API: execute=True to run code, execute=False to return code
"""

import os
import json
import getpass
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Union
import re
import warnings
warnings.filterwarnings('ignore')

# ============================================
# CORE PROMPTS
# ============================================

GENERATE_PROMPT = """You are a Python code generator. Generate clean, executable Python code based on the user's request.

Requirements:
- Return ONLY the Python code, no explanations, markdown, or duplicate outputs
- Include helpful inline comments using #
- Ensure code is syntactically correct and follows best practices
- Use appropriate imports if needed
- If creating a reusable result, store it in a variable called 'result'
- Do NOT repeat the same code multiple times
- Do NOT include example usage or duplicate implementations

Generate the code once and only once. Focus on writing clean, readable code that accomplishes the exact task requested."""

CLEAN_PROMPT = """You are a data cleaning expert. Generate Python code to clean the provided DataFrame.

Requirements:
- Return ONLY executable Python code, no explanations
- Add inline comments explaining each cleaning step
- Handle common issues: missing values, duplicates, data types, outliers
- Use pandas best practices
- Assume the DataFrame variable is named 'df'
- Store the cleaned DataFrame in a variable called 'result'

Generate practical cleaning code based on the DataFrame structure and sample data provided."""

ANALYZE_PROMPT = """You are a data analysis expert. Generate Python code to analyze the provided DataFrame.

Requirements:
- Return ONLY executable Python code, no explanations
- Add inline comments explaining each analysis step
- Include basic statistics, distributions, correlations
- Use pandas, numpy for analysis
- Assume the DataFrame variable is named 'df'
- Store analysis results in a dictionary variable called 'result'

Generate comprehensive analysis code based on the DataFrame structure and sample data provided."""

VISUALIZE_PROMPT = """You are a data visualization expert. Generate Python code to create visualizations for the provided DataFrame.

Requirements:
- Return ONLY executable Python code, no explanations
- Add inline comments explaining each visualization
- Create 2-3 most relevant plots for this dataset
- Use matplotlib/seaborn for plotting
- Assume the DataFrame variable is named 'df'
- Include plt.show() to display plots

Generate visualization code based on the DataFrame structure and sample data provided."""

ML_PROMPT = """You are a machine learning expert. Generate Python code to train a machine learning model on the provided DataFrame.

Requirements:
- Return ONLY executable Python code, no explanations
- Add inline comments explaining each step
- Handle preprocessing, splitting, training, and evaluation
- Use scikit-learn for modeling
- Assume the DataFrame variable is named 'df' and target column is provided
- Store the trained model in a variable called 'result'
- Include model evaluation metrics

Generate complete ML pipeline code based on the DataFrame structure and target column."""

# ============================================
# CONFIGURATION AND HELPERS
# ============================================

def get_config_path():
    """Get the path to store Keeya configuration."""
    home = Path.home()
    config_dir = home / ".keeya"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"

def load_config():
    """Load Keeya configuration."""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    """Save Keeya configuration."""
    config_path = get_config_path()
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def setup_api_key():
    """Simple API key setup."""
    print("\n🔑 Keeya API Key Setup")
    print("=" * 40)
    print("Get your free API key from: https://aistudio.google.com/app/apikey")
    print()
    
    api_key = getpass.getpass("Enter your Gemini API key: ").strip()
    
    if not api_key:
        raise Exception("API key cannot be empty")
        
    if not api_key.startswith("AIzaSy"):
        print("⚠️  Warning: Gemini keys typically start with 'AIzaSy'")
        confirm = input("Continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            raise Exception("API key setup cancelled")
        
    config = load_config()
    config['gemini_api_key'] = api_key
    save_config(config)
    
    print("✅ API key saved successfully!")
    return api_key

def get_gemini_api_key():
    """Get Gemini API key with simple setup."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    config = load_config()
    api_key = config.get('gemini_api_key')
    if api_key:
        return api_key
    
    print("\n⚠️  No API key found. Let's set one up!")
    return setup_api_key()

# ============================================
# API CALL FUNCTION
# ============================================

def call_gemini_api(system_prompt: str, user_prompt: str, model: str = "gemini-1.5-flash") -> str:
    """Call Google Gemini API."""
    try:
        api_key = get_gemini_api_key()
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        headers = {"Content-Type": "application/json"}
        
        full_prompt = f"{system_prompt}\n\nUser Request: {user_prompt}"
        
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "maxOutputTokens": 8192
            }
        }
        
        response = requests.post(
            f"{url}?key={api_key}", 
            headers=headers, 
            json=payload, 
            timeout=30
        )
        
        if response.status_code != 200:
            error_msg = f"API error (status {response.status_code})"
            try:
                error_detail = response.json()
                if 'error' in error_detail:
                    error_msg = f"{error_msg}: {error_detail['error'].get('message', 'Unknown error')}"
            except:
                error_msg = f"{error_msg}: {response.text[:200]}"
            raise Exception(error_msg)
        
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                parts = candidate['content']['parts']
                if len(parts) > 0 and 'text' in parts[0]:
                    text = parts[0]['text'].strip()
                    text = text.replace('```python', '').replace('```', '').strip()
                    
                    # Remove duplicate code blocks
                    lines = text.split('\n')
                    cleaned_lines = []
                    seen_lines = set()
                    
                    for line in lines:
                        line_stripped = line.strip()
                        # Skip empty lines and duplicates (but keep comments and unique code)
                        if line_stripped and not line_stripped.startswith('#'):
                            if line_stripped in seen_lines:
                                continue
                            seen_lines.add(line_stripped)
                        cleaned_lines.append(line)
                    
                    # Join back and return
                    cleaned_text = '\n'.join(cleaned_lines).strip()
                    return cleaned_text
        
        raise Exception("No text content found in API response")
        
    except Exception as e:
        if "API key not valid" in str(e):
            print("\n❌ Invalid API key. Please run: keeya.setup()")
        raise Exception(f"Failed to call Gemini API: {str(e)}")

# ============================================
# HELPER FUNCTIONS
# ============================================

def analyze_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze DataFrame and return basic information."""
    dtypes_dict = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    sample_data = {}
    for col in df.columns:
        try:
            sample_values = df[col].dropna().head(3).tolist()
            sample_data[col] = [
                str(val) if not isinstance(val, (str, int, float, bool)) else val 
                for val in sample_values
            ]
        except:
            sample_data[col] = [str(val) for val in df[col].dropna().head(3)]
    
    missing_dict = {col: int(df[col].isnull().sum()) for col in df.columns}
    
    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": dtypes_dict,
        "missing_values": missing_dict,
        "sample_data": sample_data
    }

def is_valid_python_code(code: str) -> bool:
    """Check if the response looks like valid Python code."""
    if not code or not isinstance(code, str) or len(code) < 20:
        return False
    
    code = code.strip()
    
    invalid_patterns = ["I cannot", "I'm sorry", "I apologize", "gemini"]
    for pattern in invalid_patterns:
        if pattern.lower() in code.lower()[:100]:
            return False
    
    python_indicators = ['=', 'def ', 'import ', 'for ', 'if ', '#', 'print(', '.', '(', ')']
    indicators_found = sum(1 for indicator in python_indicators if indicator in code)
    
    return indicators_found >= 3

def execute_code(code: str, context: Dict[str, Any] = None) -> Any:
    """Execute generated code and return result."""
    if context is None:
        context = {}
    
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    exec_globals = {
        "__builtins__": __builtins__,
        "pd": pd,
        "np": np,
        "plt": plt,
        "sns": sns,
        "warnings": warnings,
    }
    
    # Add sklearn if available
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler, LabelEncoder
        from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
        from sklearn.metrics import mean_squared_error, accuracy_score
        
        exec_globals.update({
            'train_test_split': train_test_split,
            'StandardScaler': StandardScaler,
            'LabelEncoder': LabelEncoder,
            'RandomForestRegressor': RandomForestRegressor,
            'RandomForestClassifier': RandomForestClassifier,
            'mean_squared_error': mean_squared_error,
            'accuracy_score': accuracy_score
        })
    except ImportError:
        pass
    
    exec_globals.update(context)
    
    try:
        exec(code, exec_globals)
        
        if 'result' in exec_globals:
            return exec_globals['result']
        
        return None
    except Exception as e:
        raise Exception(f"Code execution failed: {str(e)}")

# ============================================
# MAIN API FUNCTIONS
# ============================================

def generate(prompt: str, execute: bool = False, model: str = "gemini-1.5-flash") -> Union[str, Any]:
    """
    Generate Python code from natural language.
    
    Args:
        prompt: What you want to generate
        execute: If True, run the code and return result. If False, return code string
        model: Model to use (default: gemini-1.5-flash)
    
    Returns:
        If execute=False: Generated code string
        If execute=True: Execution result
    
    Examples:
        code = keeya.generate("calculate fibonacci")
        result = keeya.generate("calculate 2+2", execute=True)
    """
    print(f"\n🤖 Generating code...")
    
    try:
        response = call_gemini_api(GENERATE_PROMPT, prompt, model)
        
        if not is_valid_python_code(response):
            raise Exception("Invalid code generated")
        
        if execute:
            print("▶️  Executing code...")
            result = execute_code(response)
            print("✅ Done!")
            return result
        else:
            print("✨ Generated Code:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            return response
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

def clean(df: pd.DataFrame, execute: bool = False, model: str = "gemini-1.5-flash") -> Union[str, pd.DataFrame]:
    """
    Clean a DataFrame using AI-generated code.
    
    Args:
        df: DataFrame to clean
        execute: If True, return cleaned DataFrame. If False, return code
        model: Model to use
    
    Returns:
        If execute=False: Cleaning code string
        If execute=True: Cleaned DataFrame
    
    Examples:
        code = keeya.clean(df)
        cleaned_df = keeya.clean(df, execute=True)
    """
    print(f"\n🧹 Generating cleaning code...")
    
    try:
        df_info = analyze_dataframe(df)
        user_prompt = f"""Clean this DataFrame:

DataFrame Info:
{json.dumps(df_info, indent=2)}

Sample Data:
{df.head().to_string()}"""
        
        response = call_gemini_api(CLEAN_PROMPT, user_prompt, model)
        
        if not is_valid_python_code(response):
            response = generate_fallback_cleaning_code(df)
        
        if execute:
            print("▶️  Executing cleaning...")
            result = execute_code(response, {'df': df})
            if isinstance(result, pd.DataFrame):
                print(f"✅ Cleaned! Shape: {df.shape} → {result.shape}")
                return result
            else:
                print("⚠️  No DataFrame returned, returning original")
                return df
        else:
            print("✨ Cleaning Code:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            return response
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if execute:
            return df
        raise

def analyze(df: pd.DataFrame, execute: bool = True, model: str = "gemini-1.5-flash") -> Union[str, Dict]:
    """
    Analyze a DataFrame using AI.
    
    Args:
        df: DataFrame to analyze
        execute: If True, return analysis results. If False, return code
        model: Model to use
    
    Returns:
        If execute=False: Analysis code string
        If execute=True: Analysis results dictionary
    
    Examples:
        results = keeya.analyze(df)
        code = keeya.analyze(df, execute=False)
    """
    print(f"\n📊 Generating analysis...")
    
    try:
        df_info = analyze_dataframe(df)
        user_prompt = f"""Analyze this DataFrame:

DataFrame Info:
{json.dumps(df_info, indent=2)}

Sample Data:
{df.head().to_string()}"""
        
        response = call_gemini_api(ANALYZE_PROMPT, user_prompt, model)
        
        if not is_valid_python_code(response):
            response = generate_fallback_analysis_code(df)
        
        if execute:
            print("▶️  Running analysis...")
            result = execute_code(response, {'df': df})
            
            if isinstance(result, dict):
                print("\n📊 Analysis Results:")
                print("=" * 60)
                for key, value in result.items():
                    print(f"\n🔍 {key.replace('_', ' ').title()}:")
                    if isinstance(value, dict) and len(value) > 0:
                        for k, v in list(value.items())[:5]:
                            print(f"  {k}: {v}")
                        if len(value) > 5:
                            print(f"  ... and {len(value)-5} more")
                    elif isinstance(value, (list, tuple)):
                        for item in value[:5]:
                            print(f"  • {item}")
                        if len(value) > 5:
                            print(f"  ... and {len(value)-5} more")
                    else:
                        print(f"  {value}")
                print("=" * 60)
                return result
            else:
                # Fallback if no dict returned
                basic_results = {
                    'shape': df.shape,
                    'columns': list(df.columns),
                    'dtypes': df.dtypes.to_dict(),
                    'missing': df.isnull().sum().to_dict(),
                    'summary': df.describe().to_dict() if not df.select_dtypes(include=[np.number]).empty else {}
                }
                return basic_results
        else:
            print("✨ Analysis Code:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            return response
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if execute:
            return {'error': str(e)}
        raise

def visualize(df: pd.DataFrame, plot_type: str = None, execute: bool = False, model: str = "gemini-1.5-flash") -> Union[str, None]:
    """
    Create visualizations for a DataFrame.
    
    Args:
        df: DataFrame to visualize
        plot_type: Type of plot (optional)
        execute: If True, display plots. If False, return code
        model: Model to use
    
    Returns:
        If execute=False: Visualization code string
        If execute=True: None (plots are displayed)
    
    Examples:
        code = keeya.visualize(df)
        keeya.visualize(df, execute=True)
        keeya.visualize(df, "correlation", execute=True)
    """
    print(f"\n📈 Generating visualization code...")
    
    try:
        df_info = analyze_dataframe(df)
        user_prompt = f"""Create visualizations for this DataFrame:

DataFrame Info:
{json.dumps(df_info, indent=2)}

Sample Data:
{df.head().to_string()}"""
        
        if plot_type:
            user_prompt += f"\n\nFocus on {plot_type} plots"
        
        response = call_gemini_api(VISUALIZE_PROMPT, user_prompt, model)
        
        if not is_valid_python_code(response):
            response = generate_fallback_visualization_code(df, plot_type)
        
        if execute:
            print("▶️  Creating visualizations...")
            execute_code(response, {'df': df})
            print("✅ Plots displayed!")
            return None
        else:
            print("✨ Visualization Code:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            return response
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

def train(df: pd.DataFrame, target: str, execute: bool = False, model: str = "gemini-1.5-flash") -> Union[str, Any]:
    """
    Train a machine learning model on a DataFrame.
    
    Args:
        df: DataFrame with features and target
        target: Name of target column
        execute: If True, return trained model. If False, return code
        model: Model to use for code generation
    
    Returns:
        If execute=False: ML pipeline code string
        If execute=True: Trained model object
    
    Examples:
        code = keeya.train(df, "price")
        model = keeya.train(df, "price", execute=True)
    """
    print(f"\n🤖 Generating ML pipeline...")
    
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in DataFrame")
    
    try:
        df_info = analyze_dataframe(df)
        target_info = {
            'dtype': str(df[target].dtype),
            'unique_values': df[target].nunique(),
            'sample_values': df[target].dropna().head(5).tolist()
        }
        
        user_prompt = f"""Create a machine learning pipeline for this DataFrame:

DataFrame Info:
{json.dumps(df_info, indent=2)}

Target Column: {target}
Target Info: {json.dumps(target_info, indent=2)}

Sample Data:
{df.head().to_string()}"""
        
        response = call_gemini_api(ML_PROMPT, user_prompt, model)
        
        if not is_valid_python_code(response):
            response = generate_fallback_ml_code(df, target)
        
        if execute:
            print("▶️  Training model...")
            result = execute_code(response, {'df': df, 'target': target})
            print("✅ Model trained successfully!")
            return result
        else:
            print("✨ ML Pipeline Code:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            return response
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

# ============================================
# FALLBACK FUNCTIONS
# ============================================

def generate_fallback_cleaning_code(df: pd.DataFrame) -> str:
    """Generate basic cleaning code when AI fails."""
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    object_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    return f"""
# Basic DataFrame cleaning
import pandas as pd
import numpy as np

# Create a copy
result = df.copy()

# Remove duplicates
result = result.drop_duplicates()

# Handle missing values in numeric columns
numeric_cols = {numeric_cols}
for col in numeric_cols:
    if col in result.columns:
        median_val = result[col].median()
        if pd.notna(median_val):
            result[col] = result[col].fillna(median_val)

# Handle missing values in text columns  
object_cols = {object_cols}
for col in object_cols:
    if col in result.columns:
        result[col] = result[col].fillna('Unknown')

# Reset index
result = result.reset_index(drop=True)

print(f"Cleaned: {{df.shape}} → {{result.shape}}")
"""

def generate_fallback_analysis_code(df: pd.DataFrame) -> str:
    """Generate basic analysis code when AI fails."""
    return """
# Basic DataFrame analysis
import pandas as pd
import numpy as np

result = {
    'shape': df.shape,
    'columns': list(df.columns),
    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
    'missing_values': df.isnull().sum().to_dict(),
    'unique_counts': {col: df[col].nunique() for col in df.columns}
}

# Add numeric summaries if available
numeric_cols = df.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 0:
    result['summary'] = df[numeric_cols].describe().to_dict()

print("Analysis complete")
"""

def generate_fallback_visualization_code(df: pd.DataFrame, plot_type: str = None) -> str:
    """Generate basic visualization code when AI fails."""
    return """
# Basic DataFrame visualizations
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(12, 4))

# Plot 1: First numeric column distribution
numeric_cols = df.select_dtypes(include=['number']).columns
if len(numeric_cols) > 0:
    plt.subplot(1, 3, 1)
    plt.hist(df[numeric_cols[0]].dropna(), bins=20, edgecolor='black')
    plt.title(f'Distribution of {numeric_cols[0]}')
    plt.xlabel(numeric_cols[0])
    plt.ylabel('Frequency')

# Plot 2: Missing values
plt.subplot(1, 3, 2)
missing = df.isnull().sum()
missing = missing[missing > 0]
if not missing.empty:
    missing.plot(kind='bar')
    plt.title('Missing Values')
    plt.ylabel('Count')
    plt.xticks(rotation=45)

# Plot 3: Correlation heatmap (if multiple numeric columns)
if len(numeric_cols) > 1:
    plt.subplot(1, 3, 3)
    corr_matrix = df[numeric_cols].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, square=True)
    plt.title('Correlations')

plt.tight_layout()
plt.show()
"""

def generate_fallback_ml_code(df: pd.DataFrame, target: str) -> str:
    """Generate basic ML code when AI fails."""
    return f"""
# Basic ML Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score
import numpy as np
import pandas as pd

# Prepare data
X = df.drop(columns=['{target}'])
y = df['{target}']

# Remove rows with missing target
mask = y.notna()
X = X[mask]
y = y[mask]

# Handle categorical features
for col in X.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    X.loc[:, col] = le.fit_transform(X[col].fillna('missing'))

# Handle numeric features
numeric_cols = X.select_dtypes(include=['number']).columns
X[numeric_cols] = X[numeric_cols].fillna(X[numeric_cols].median())

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train model
if y.nunique() < 10:
    result = RandomForestClassifier(n_estimators=100, random_state=42)
    result.fit(X_train, y_train)
    score = accuracy_score(y_test, result.predict(X_test))
    print(f"Accuracy: {{score:.4f}}")
else:
    result = RandomForestRegressor(n_estimators=100, random_state=42)
    result.fit(X_train, y_train)
    score = mean_squared_error(y_test, result.predict(X_test), squared=False)
    print(f"RMSE: {{score:.4f}}")

print(f"Model trained on {{len(X_train)}} samples")
"""

# ============================================
# UTILITY FUNCTIONS
# ============================================

def setup():
    """Set up or change your Gemini API key."""
    print("\n🚀 Welcome to Keeya Setup!")
    print("=" * 40)
    
    config = load_config()
    if 'gemini_api_key' in config:
        print("ℹ️  An API key is already configured.")
        choice = input("Do you want to replace it? (y/n): ")
        if choice.lower() != 'y':
            print("Setup cancelled.")
            return
        config = {}
        save_config(config)
    
    try:
        setup_api_key()
        print("\n✅ Setup complete!")
        print("\nTry these commands:")
        print('  keeya.generate("hello world")')
        print('  keeya.clean(df, execute=True)')
        print('  keeya.analyze(df)')
        
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")

def help():
    """Display help information."""
    print("\n" + "="*60)
    print("KEEYA - Simple AI-Powered Data Tool")
    print("="*60)
    print("\n🎯 Core Pattern: execute=True runs code, execute=False returns code\n")
    
    print("📚 Functions:\n")
    functions = [
        ("generate(prompt, execute=False)", "Generate Python code"),
        ("clean(df, execute=False)", "Clean a DataFrame"),
        ("analyze(df, execute=True)", "Analyze a DataFrame"),
        ("visualize(df, execute=False)", "Create visualizations"),
        ("train(df, target, execute=False)", "Train ML model"),
        ("setup()", "Configure API key"),
        ("help()", "Show this help"),
    ]
    
    for func, desc in functions:
        print(f"  {func:<35} {desc}")
    
    print("\n💡 Examples:\n")
    print('  code = keeya.generate("calculate fibonacci")')
    print('  result = keeya.generate("return 2+2", execute=True)')
    print('  cleaned_df = keeya.clean(df, execute=True)')
    print('  results = keeya.analyze(df)')
    print('  keeya.visualize(df, execute=True)')
    
    print("\n🔗 Get your free API key at:")
    print("   https://aistudio.google.com/app/apikey")
    print("="*60)

# Print welcome message
print("🎉 Keeya loaded! | keeya.help() for usage | keeya.setup() to configure")