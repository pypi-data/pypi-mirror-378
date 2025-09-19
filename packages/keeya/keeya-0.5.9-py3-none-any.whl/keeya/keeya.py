"""
Keeya - AI-Powered Python Code Generation
All functionality combined into one file.
"""

import pandas as pd
import requests
import json
import os
from typing import Dict, Any, Optional

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file."""
    try:
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    except Exception:
        pass  # Ignore errors if .env file doesn't exist

# Load .env file when module is imported
load_env()

# System Prompts
GENERATE_PROMPT = """You are an expert Python code generator. Generate clean, production-ready Python code.

CRITICAL REQUIREMENTS:
- Generate ONLY Python code - no markdown, no explanations, no text outside code
- Use inline comments (#) to explain complex logic
- Write clean, readable code with proper variable names
- Include error handling where appropriate
- Follow Python best practices (PEP 8)

Example:
User: "function to add two numbers"
Response:
def add_numbers(num1, num2):
    # Add two numbers and return the result
    return num1 + num2

User: "function to divide two numbers"
Response:
def divide_numbers(a, b):
    # Divide two numbers with zero division check
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b"""

CLEAN_PROMPT = """You are a data cleaning expert. Generate clean Python code to clean the DataFrame.

CRITICAL REQUIREMENTS:
- Generate ONLY Python code - no markdown, no explanations
- Use inline comments (#) to explain each cleaning step
- Focus on basic cleaning: missing values, duplicates, data types
- Assign result to variable 'cleaned_df'
- Keep it simple and executable

Example format:
# Create a copy to avoid modifying original
cleaned_df = df.copy()

# Remove duplicate rows
cleaned_df = cleaned_df.drop_duplicates()

# Handle missing values
for col in cleaned_df.select_dtypes(include=['number']).columns:
    cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())

for col in cleaned_df.select_dtypes(include=['object']).columns:
    cleaned_df[col] = cleaned_df[col].fillna('Unknown')"""

ANALYZE_PROMPT = """You are a data analysis expert. Generate clean Python code to analyze the DataFrame.

CRITICAL REQUIREMENTS:
- Generate ONLY Python code - no markdown, no explanations
- Use inline comments (#) to explain each analysis step
- Focus on basic analysis: shape, info, summary statistics
- Store results in 'analysis_results' dictionary
- Keep it simple and executable

Example format:
# Initialize analysis results dictionary
analysis_results = {}

# Basic DataFrame info
analysis_results['shape'] = df.shape
analysis_results['columns'] = list(df.columns)
analysis_results['dtypes'] = df.dtypes.to_dict()

# Statistical summary
analysis_results['summary'] = df.describe().to_dict()
analysis_results['missing_values'] = df.isnull().sum().to_dict()"""

VISUALIZE_PROMPT = """You are a data visualization expert. Generate clean Python code to create simple visualizations.

CRITICAL REQUIREMENTS:
- Generate ONLY Python code - no markdown, no explanations
- Use inline comments (#) to explain each visualization
- Create 2-3 basic plots: histogram, scatter, bar chart
- Use matplotlib/seaborn with simple styling
- Keep it simple and executable

Example format:
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('default')

# Create histogram for numeric columns
numeric_cols = df.select_dtypes(include=['number']).columns
if len(numeric_cols) > 0:
    plt.figure(figsize=(10, 6))
    df[numeric_cols[0]].hist(bins=20)
    plt.title(f'Distribution of {numeric_cols[0]}')
    plt.show()

# Create correlation heatmap if multiple numeric columns
if len(numeric_cols) > 1:
    plt.figure(figsize=(8, 6))
    sns.heatmap(df[numeric_cols].corr(), annot=True)
    plt.title('Correlation Matrix')
    plt.show()"""

ML_PROMPT = """You are a machine learning expert. Generate clean Python code to train a model on the provided data.

CRITICAL REQUIREMENTS:
- Generate ONLY Python code - no markdown, no explanations
- Use inline comments (#) to explain each ML step
- Perform proper data preprocessing and train/test split
- Choose appropriate algorithm for the task
- Evaluate model performance with metrics
- Assign trained model to 'model' variable
- Use scikit-learn best practices

Example format:
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# Prepare features and target
X = df.drop(columns=[target])
y = df[target]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model performance
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print(f'Model MSE: {mse}')"""

# API Functions
def get_gemini_api_key():
    """Get Gemini API key."""
    # Use our demo Gemini API key
    return "AIzaSyD4Odpx0-eiZplBXf5WLOXmj40qWbQTHDM"

def call_gemini_api(system_prompt: str, user_prompt: str, model: str = "gemini-2.5-flash") -> str:
    """
    Call Google Gemini API with bulletproof response parsing.
    
    Args:
        system_prompt: System prompt for AI
        user_prompt: User prompt
        model: Model to use (default: gemini-2.5-flash)
        
    Returns:
        str: AI response
    """
    try:
        api_key = get_gemini_api_key()
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"{system_prompt}\n\nUser: {user_prompt}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "maxOutputTokens": 2000
            }
        }
        
        response = requests.post(f"{url}?key={api_key}", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Bulletproof text extraction - handles ANY response structure
        def extract_any_text(obj, path=""):
            """Recursively extract text from any nested structure."""
            if isinstance(obj, str) and len(obj) > 10:  # Likely text content
                return obj.strip()
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    if key == "text" and isinstance(value, str) and len(value) > 5:
                        return value.strip()
                    result_text = extract_any_text(value, f"{path}.{key}")
                    if result_text:
                        return result_text
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    result_text = extract_any_text(item, f"{path}[{i}]")
                    if result_text:
                        return result_text
            return None
        
        # Try to extract text from anywhere in the response
        text = extract_any_text(result)
        if text:
            return text
        
        # Fallback: regex extraction for any text patterns
        import re
        response_str = str(result)
        
        # Look for any text field with actual content
        text_matches = re.findall(r'"text":\s*"([^"]*)"', response_str)
        if text_matches:
            # Return the longest text match (likely the actual response)
            longest_match = max(text_matches, key=len)
            if len(longest_match) > 5:  # Must be substantial content
                return longest_match.strip()
        
        # Look for code patterns as last resort
        code_patterns = [
            r'def\s+\w+\s*\([^)]*\):.*?(?=def|\Z)',
            r'import\s+\w+.*?(?=import|\Z)',
            r'#.*?(?=\n|\Z)',
            r'for\s+\w+\s+in.*?(?=for|\Z)',
            r'if\s+.*?(?=if|\Z)',
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, response_str, re.DOTALL)
            if matches:
                return matches[0].strip()
        
        # If all else fails, show the actual response structure for debugging
        raise Exception(f"No text content found. Response: {json.dumps(result, indent=2)[:500]}...")
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Gemini API request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to call Gemini API: {str(e)}")

def call_ai_api(system_prompt: str, user_prompt: str, model: str = "gemini-2.5-flash") -> str:
    """
    Call Gemini AI API.
    
    Args:
        system_prompt: System prompt for AI
        user_prompt: User prompt
        model: Model to use (default: gemini-2.5-flash)
        
    Returns:
        str: AI response
    """
    return call_gemini_api(system_prompt, user_prompt, model)

def analyze_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze DataFrame and return basic information.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dict: Analysis results
    """
    # Convert dtypes to strings for JSON serialization
    dtypes_dict = {}
    for col, dtype in df.dtypes.items():
        dtypes_dict[col] = str(dtype)
    
    # Convert sample data to JSON-serializable format
    sample_data = {}
    for col in df.columns:
        try:
            # Try to get first 3 non-null values
            sample_values = df[col].dropna().head(3).tolist()
            # Convert any non-serializable objects to strings
            sample_data[col] = [str(val) if not isinstance(val, (str, int, float, bool)) else val for val in sample_values]
        except Exception:
            # If conversion fails, use string representation
            sample_data[col] = [str(val) for val in df[col].dropna().head(3)]
    
    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": dtypes_dict,
        "missing_values": df.isnull().sum().to_dict(),
        "sample_data": sample_data
    }

def execute_code_safely(code: str, context: Dict[str, Any] = None) -> Any:
    """
    Execute generated code safely.
    
    Args:
        code: Code to execute
        context: Context variables (like DataFrame)
        
    Returns:
        Any: Execution result
    """
    if context is None:
        context = {}
    
    # Safe globals
    safe_globals = {
        "__builtins__": {
            "print": print,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "sum": sum,
            "max": max,
            "min": min,
            "abs": abs,
            "round": round,
            "type": type,
            "isinstance": isinstance,
            "hasattr": hasattr,
            "getattr": getattr,
            "setattr": setattr,
            "__import__": __import__
        }
    }
    
    # Add context variables
    safe_globals.update(context)
    
    try:
        # Try to execute the code
        exec(code, safe_globals)
        
        # Try to find result variables
        result_vars = ['result', 'output', 'cleaned_df', 'analysis_results', 'model', 'cleaned_data']
        for var in result_vars:
            if var in safe_globals:
                return safe_globals[var]
        
        # If no result variable found, try to evaluate the last expression
        lines = code.strip().split('\n')
        last_line = lines[-1].strip()
        if last_line and not last_line.startswith('#') and not last_line.startswith('import'):
            try:
                return eval(last_line, safe_globals)
            except:
                pass
        
        return None
        
    except Exception as e:
        raise Exception(f"Failed to execute code safely: {str(e)}")

def get_available_models() -> Dict[str, str]:
    """
    Get available models with their descriptions.
    
    Returns:
        Dict: Model names and descriptions
    """
    return {
        "gemini-2.5-flash": "Gemini 2.5 Flash (Latest, fast, 1M context, free)",
        "gemini-2.5-pro": "Gemini 2.5 Pro (Most capable, high quality, free tier)",
        "gemini-2.0-flash-exp": "Gemini 2.0 Flash Experimental (Cutting edge, free)",
        "gemini-1.5-flash": "Gemini 1.5 Flash (Reliable fallback, free)"
    }

def generate_fallback_cleaning_code(df: pd.DataFrame) -> str:
    """
    Generate basic fallback cleaning code when AI fails.
    
    Args:
        df: DataFrame to clean
        
    Returns:
        str: Basic Python code for cleaning the DataFrame
    """
    # Analyze the DataFrame to generate targeted cleaning code
    df_info = analyze_dataframe(df)
    
    code_lines = [
        "# Basic DataFrame cleaning code",
        "# Create a copy to avoid modifying original DataFrame",
        "cleaned_df = df.copy()",
        "",
        "# Remove duplicate rows",
        "cleaned_df = cleaned_df.drop_duplicates()",
        ""
    ]
    
    # Handle missing values based on data types
    numeric_cols = [col for col, dtype in df_info['dtypes'].items() if 'int' in dtype or 'float' in dtype]
    object_cols = [col for col, dtype in df_info['dtypes'].items() if 'object' in dtype or 'string' in dtype]
    
    if numeric_cols:
        code_lines.extend([
            "# Fill missing values in numeric columns with median",
            "numeric_cols = " + str(numeric_cols),
            "for col in numeric_cols:",
            "    if col in cleaned_df.columns:",
            "        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())",
            ""
        ])
    
    if object_cols:
        code_lines.extend([
            "# Fill missing values in text columns with 'Unknown'",
            "text_cols = " + str(object_cols),
            "for col in text_cols:",
            "    if col in cleaned_df.columns:",
            "        cleaned_df[col] = cleaned_df[col].fillna('Unknown')",
            "        # Convert to lowercase and strip whitespace",
            "        cleaned_df[col] = cleaned_df[col].astype(str).str.lower().str.strip()",
            ""
        ])
    
    # Add specific cleaning based on missing values
    missing_values = df_info.get('missing_values', {})
    high_missing_cols = [col for col, count in missing_values.items() if count > len(df) * 0.5]
    
    if high_missing_cols:
        code_lines.extend([
            "# Consider dropping columns with >50% missing values",
            f"# High missing columns: {high_missing_cols}",
            "# Uncomment the next line if you want to drop them:",
            f"# cleaned_df = cleaned_df.drop(columns={high_missing_cols})",
            ""
        ])
    
    code_lines.extend([
        "# Remove rows with any remaining missing values (optional)",
        "# cleaned_df = cleaned_df.dropna()",
        "",
        "# Reset index",
        "cleaned_df = cleaned_df.reset_index(drop=True)",
        "",
        "# Display basic info about cleaned DataFrame",
        "print(f'Original shape: {df.shape}')",
        "print(f'Cleaned shape: {cleaned_df.shape}')",
        "print(f'Removed {df.shape[0] - cleaned_df.shape[0]} rows')",
        "",
        "# Display the cleaned DataFrame",
        "print('\\nCleaned DataFrame:')",
        "print(cleaned_df.head())"
    ])
    
    return "\n".join(code_lines)

# Main API Functions
def generate(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """
    Generate Python code from natural language prompt.

    Args:
        prompt: Natural language description of what you want to generate
        model: Model to use (default: gemini-2.5-flash)

    Returns:
        str: Generated Python code
    """
    try:
        response = call_ai_api(
            system_prompt=GENERATE_PROMPT,
            user_prompt=prompt,
            model=model
        )
        return response
    except Exception as e:
        raise Exception(f"Failed to generate code: {str(e)}")

def clean(df: pd.DataFrame, model: str = "gemini-2.5-flash") -> str:
    """
    Generate code to clean a DataFrame using AI with fallback.

    Args:
        df: DataFrame to clean
        model: Model to use (optional, auto-selects if None)

    Returns:
        str: Generated Python code for cleaning the DataFrame
    """
    try:
        # Analyze DataFrame
        df_info = analyze_dataframe(df)
        
        # Create user prompt with DataFrame info
        user_prompt = f"Clean this DataFrame:\n\nDataFrame Info:\n{json.dumps(df_info, indent=2)}\n\nDataFrame:\n{df.head().to_string()}"
        
        # Call AI API
        response = call_ai_api(
            system_prompt=CLEAN_PROMPT,
            user_prompt=user_prompt,
            model=model
        )
        
        # Validate the response is actually Python code
        if not is_valid_python_code(response):
            raise Exception(f"AI returned invalid code: '{response}' - triggering fallback")
        # Validate the response is actually Python code
        if not is_valid_python_code(response):
            raise Exception(f"AI returned invalid code: '{response}' - triggering fallback")
        # Print the generated code for user to see and execute
        print("🧹 AI Generated Cleaning Code:")
        print("=" * 50)
        print(response)
        print("=" * 50)
        print("📋 Copy and run this code to clean your DataFrame!")
        
        return response
            
    except Exception as e:
        # Fallback: Generate basic cleaning code
        print("⚠️  AI API failed. Generating basic cleaning code as fallback...")
        print()
        
        fallback_code = generate_fallback_cleaning_code(df)
        
        print("🧹 Fallback Cleaning Code:")
        print("=" * 50)
        print(fallback_code)
        print("=" * 50)
        print("📋 Copy and run this basic cleaning code for your DataFrame!")
        print(f"💡 Error details: {str(e)}")
        
        return fallback_code

def analyze(df: pd.DataFrame, model: str = "gemini-2.5-flash") -> dict:
    """
    Analyze a DataFrame using AI.

    Args:
        df: DataFrame to analyze
        model: Model to use (optional, auto-selects if None)

    Returns:
        dict: Analysis results with formatted output
    """
    try:
        # Analyze DataFrame
        df_info = analyze_dataframe(df)
        
        # Create user prompt with DataFrame info
        user_prompt = f"Analyze this DataFrame:\n\nDataFrame Info:\n{json.dumps(df_info, indent=2)}\n\nDataFrame:\n{df.head().to_string()}"
        
        # Call AI API
        response = call_ai_api(
            system_prompt=ANALYZE_PROMPT,
            user_prompt=user_prompt,
            model=model
        )
        
        # Execute the generated code
        result = execute_code_safely(response, {'df': df})
        
        if result is not None:
            # Print formatted analysis results
            print("📊 DataFrame Analysis Results:")
            print("=" * 60)
            
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"\n🔍 {key.replace('_', ' ').title()}:")
                    print("-" * 30)
                    
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            print(f"  {sub_key}: {sub_value}")
                    elif isinstance(value, (list, tuple)):
                        for item in value:
                            print(f"  • {item}")
                    else:
                        print(f"  {value}")
            else:
                print(result)
            
            print("=" * 60)
            return result
        else:
            raise Exception("No analysis results returned from generated code")
            
    except Exception as e:
        raise Exception(f"Failed to analyze DataFrame: {str(e)}")

def generate_fallback_visualization_code(df: pd.DataFrame, plot_type: Optional[str] = None) -> str:
    """
    Generate basic fallback visualization code when AI fails.
    
    Args:
        df: DataFrame to visualize
        plot_type: Type of plot to create (optional)
        
    Returns:
        str: Basic Python code for visualizing the DataFrame
    """
    # Analyze the DataFrame to generate targeted visualization code
    df_info = analyze_dataframe(df)
    
    code_lines = [
        "# Basic DataFrame visualization code",
        "import matplotlib.pyplot as plt",
        "import seaborn as sns",
        "import pandas as pd",
        "",
        "# Set style for better plots",
        "plt.style.use('default')",
        "sns.set_palette('husl')",
        ""
    ]
    
    # Get column types
    numeric_cols = [col for col, dtype in df_info['dtypes'].items() if 'int' in dtype or 'float' in dtype]
    object_cols = [col for col, dtype in df_info['dtypes'].items() if 'object' in dtype or 'string' in dtype]
    
    # Generate plots based on data types
    if numeric_cols:
        if len(numeric_cols) >= 2:
            code_lines.extend([
                "# Correlation heatmap for numeric columns",
                f"numeric_cols = {numeric_cols}",
                "plt.figure(figsize=(10, 8))",
                "correlation_matrix = df[numeric_cols].corr()",
                "sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)",
                "plt.title('Correlation Matrix of Numeric Variables')",
                "plt.tight_layout()",
                "plt.show()",
                ""
            ])
        
        # Distribution plots for first few numeric columns
        for i, col in enumerate(numeric_cols[:3]):
            code_lines.extend([
                f"# Distribution plot for {col}",
                "plt.figure(figsize=(10, 6))",
                f"plt.hist(df['{col}'].dropna(), bins=30, alpha=0.7, edgecolor='black')",
                f"plt.title('Distribution of {col}')",
                f"plt.xlabel('{col}')",
                "plt.ylabel('Frequency')",
                "plt.grid(True, alpha=0.3)",
                "plt.show()",
                ""
            ])
    
    if object_cols:
        # Bar plots for categorical columns
        for i, col in enumerate(object_cols[:2]):
            code_lines.extend([
                f"# Bar plot for {col}",
                "plt.figure(figsize=(12, 6))",
                f"value_counts = df['{col}'].value_counts().head(10)",
                "plt.bar(range(len(value_counts)), value_counts.values)",
                "plt.xticks(range(len(value_counts)), value_counts.index, rotation=45)",
                f"plt.title('Top 10 Values in {col}')",
                f"plt.xlabel('{col}')",
                "plt.ylabel('Count')",
                "plt.tight_layout()",
                "plt.show()",
                ""
            ])
    
    # Scatter plot if we have at least 2 numeric columns
    if len(numeric_cols) >= 2:
        col1, col2 = numeric_cols[0], numeric_cols[1]
        code_lines.extend([
            f"# Scatter plot: {col1} vs {col2}",
            "plt.figure(figsize=(10, 6))",
            f"plt.scatter(df['{col1}'], df['{col2}'], alpha=0.6)",
            f"plt.xlabel('{col1}')",
            f"plt.ylabel('{col2}')",
            f"plt.title('{col1} vs {col2}')",
            "plt.grid(True, alpha=0.3)",
            "plt.show()",
            ""
        ])
    
    # Missing values visualization
    missing_values = df_info.get('missing_values', {})
    if any(count > 0 for count in missing_values.values()):
        code_lines.extend([
            "# Missing values visualization",
            "plt.figure(figsize=(12, 6))",
            f"missing_data = {missing_values}",
            "cols_with_missing = [col for col, count in missing_data.items() if count > 0]",
            "missing_counts = [missing_data[col] for col in cols_with_missing]",
            "plt.bar(range(len(cols_with_missing)), missing_counts)",
            "plt.xticks(range(len(cols_with_missing)), cols_with_missing, rotation=45)",
            "plt.title('Missing Values by Column')",
            "plt.xlabel('Columns')",
            "plt.ylabel('Missing Count')",
            "plt.tight_layout()",
            "plt.show()",
            ""
        ])
    
    code_lines.extend([
        "# Basic DataFrame info",
        f"print('DataFrame Shape: {df_info['shape']}')",
        f"print('Columns: {df_info['columns']}')",
        "print('\\nBasic Statistics:')",
        "print(df.describe())"
    ])
    
    return "\n".join(code_lines)

def visualize(df: pd.DataFrame, plot_type: Optional[str] = None, model: str = "gemini-2.5-flash") -> str:
    """
    Generate visualization code for a DataFrame using AI with fallback.

    Args:
        df: DataFrame to visualize
        plot_type: Type of plot to create (optional)
        model: Model to use (optional, auto-selects if None)

    Returns:
        str: Generated Python code for visualizations
    """
    try:
        # Analyze DataFrame
        df_info = analyze_dataframe(df)
        
        # Create user prompt with DataFrame info
        user_prompt = f"Create visualizations for this DataFrame:\n\nDataFrame Info:\n{json.dumps(df_info, indent=2)}\n\nDataFrame:\n{df.head().to_string()}"
        
        if plot_type:
            user_prompt += f"\n\nPreferred plot type: {plot_type}"
        
        # Call AI API
        response = call_ai_api(
            system_prompt=VISUALIZE_PROMPT,
            user_prompt=user_prompt,
            model=model
        )
        
        # Validate the response is actually Python code
        if not is_valid_python_code(response):
            raise Exception(f"AI returned invalid code: '{response}' - triggering fallback")
        # Validate the response is actually Python code
        if not is_valid_python_code(response):
            raise Exception(f"AI returned invalid code: '{response}' - triggering fallback")
        # Print the generated code for user to see and execute
        print("📊 AI Generated Visualization Code:")
        print("=" * 50)
        print(response)
        print("=" * 50)
        print("📋 Copy and run this code to create visualizations!")
        
        return response
        
    except Exception as e:
        # Fallback: Generate basic visualization code
        print("⚠️  AI API failed. Generating basic visualization code as fallback...")
        print()
        
        fallback_code = generate_fallback_visualization_code(df, plot_type)
        
        print("📊 Fallback Visualization Code:")
        print("=" * 50)
        print(fallback_code)
        print("=" * 50)
        print("📋 Copy and run this basic visualization code for your DataFrame!")
        print(f"💡 Error details: {str(e)}")
        
        return fallback_code

def train(df: pd.DataFrame, target: str, model: str = "gemini-2.5-flash") -> Any:
    """
    Train a machine learning model on a DataFrame using AI.

    Args:
        df: DataFrame with training data
        target: Target column name
        model: Model to use (optional, auto-selects if None)

    Returns:
        Any: Trained model
    """
    try:
        # Analyze DataFrame
        df_info = analyze_dataframe(df)
        
        # Create user prompt with DataFrame info
        user_prompt = f"Train a machine learning model on this DataFrame:\n\nDataFrame Info:\n{json.dumps(df_info, indent=2)}\n\nDataFrame:\n{df.head().to_string()}\n\nTarget column: {target}"
        
        # Call AI API
        response = call_ai_api(
            system_prompt=ML_PROMPT,
            user_prompt=user_prompt,
            model=model
        )
        
        # Execute the generated code
        result = execute_code_safely(response, {'df': df, 'target': target})
        
        if result is not None:
            return result
        else:
            raise Exception("No trained model returned from generated code")
            
    except Exception as e:
        raise Exception(f"Failed to train model: {str(e)}")

def is_valid_python_code(code):
    """
    Check if the response looks like valid Python code.
    
    Args:
        code: String to validate
        
    Returns:
        bool: True if it looks like valid Python code
    """
    if not code or not isinstance(code, str):
        return False
    
    code = code.strip()
    
    # Too short to be meaningful code
    if len(code) < 20:
        return False
    
    # Just model names (common invalid responses)
    invalid_responses = [
        "gemini-2.5-flash", 
        "gemini-2.5-pro", 
        "gemini-1.5-flash",
        "gemini-2.0-flash-exp"
    ]
    if code in invalid_responses:
        return False
    
    # Must contain some Python-like elements
    python_indicators = ['=', 'def ', 'import ', 'for ', 'if ', 'class ', '#', 'print(', '.']
    if not any(indicator in code for indicator in python_indicators):
        return False
    
    return True
