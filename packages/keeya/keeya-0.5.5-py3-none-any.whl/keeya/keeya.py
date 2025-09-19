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
    Call Google Gemini API.
    
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
        
        if "candidates" in result and len(result["candidates"]) > 0:
            candidate = result["candidates"][0]
            
            # Try different response structures
            try:
                # Try standard structure first
                if "content" in candidate and "parts" in candidate["content"]:
                    content = candidate["content"]["parts"][0]["text"]
                # Try direct content access
                elif "content" in candidate and "text" in candidate["content"]:
                    content = candidate["content"]["text"]
                # Try direct text access in candidate
                elif "text" in candidate:
                    content = candidate["text"]
                # Try alternative structure
                elif "content" in candidate:
                    content_obj = candidate["content"]
                    if isinstance(content_obj, str):
                        content = content_obj
                    elif isinstance(content_obj, dict) and "text" in content_obj:
                        content = content_obj["text"]
                    else:
                        raise Exception("Unexpected content structure")
                else:
                    raise Exception("No recognizable content structure")
                    
                return content.strip() if content else ""
                
            except Exception as e:
                # Fallback: try to extract any text content
                candidate_str = str(candidate)
                if "text" in candidate_str:
                    # Last resort: look for text patterns
                    import re
                    text_matches = re.findall(r'"text":\s*"([^"]*)"', candidate_str)
                    if text_matches:
                        return text_matches[0]
                
                raise Exception(f"Could not parse response structure: {str(e)}")
        else:
            raise Exception("No response from Gemini API")
            
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
    Generate code to clean a DataFrame using AI.

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
        
        # Print the generated code for user to see and execute
        print("🧹 Generated Cleaning Code:")
        print("=" * 50)
        print(response)
        print("=" * 50)
        print("📋 Copy and run this code to clean your DataFrame!")
        
        return response
            
    except Exception as e:
        raise Exception(f"Failed to generate cleaning code: {str(e)}")

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

def visualize(df: pd.DataFrame, plot_type: Optional[str] = None, model: str = "gemini-2.5-flash") -> None:
    """
    Create visualizations for a DataFrame using AI.

    Args:
        df: DataFrame to visualize
        plot_type: Type of plot to create (optional)
        model: Model to use (optional, auto-selects if None)

    Returns:
        None: Creates and displays plots
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
        
        # Execute the generated code
        execute_code_safely(response, {'df': df})
        
    except Exception as e:
        raise Exception(f"Failed to create visualizations: {str(e)}")

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
