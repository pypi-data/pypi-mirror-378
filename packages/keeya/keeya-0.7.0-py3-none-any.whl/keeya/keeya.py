import os
import json
import getpass
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
import re
import warnings
warnings.filterwarnings('ignore')

# System prompts for different tasks
GENERATE_PROMPT = """You are a Python code generator. Generate clean, executable Python code based on the user's request.

Requirements:
- Return ONLY the Python code, no explanations or markdown
- Include helpful inline comments using #
- Ensure code is syntactically correct and follows best practices
- Use appropriate imports if needed
- Make code production-ready

Focus on writing clean, readable code that accomplishes the exact task requested."""

CLEAN_PROMPT = """You are a data cleaning expert. Generate Python code to clean the provided DataFrame.

Requirements:
- Return ONLY executable Python code, no explanations
- Add inline comments explaining each cleaning step
- Handle common issues: missing values, duplicates, data types, outliers
- Use pandas best practices
- Assume the DataFrame variable is named 'df'
- Focus on the most impactful cleaning steps for this specific dataset

Generate practical cleaning code based on the DataFrame structure and sample data provided."""

ANALYZE_PROMPT = """You are a data analysis expert. Generate Python code to analyze the provided DataFrame.

Requirements:
- Return ONLY executable Python code, no explanations
- Add inline comments explaining each analysis step
- Include basic statistics, distributions, correlations
- Use pandas, numpy for analysis
- Assume the DataFrame variable is named 'df'
- Focus on insights relevant to this specific dataset
- Store results in a dictionary variable called 'analysis_results'

Generate comprehensive analysis code based on the DataFrame structure and sample data provided."""

VISUALIZE_PROMPT = """You are a data visualization expert. Generate Python code to create visualizations for the provided DataFrame.

Requirements:
- Return ONLY executable Python code, no explanations
- Add inline comments explaining each visualization
- Create 2-3 most relevant plots for this dataset
- Use matplotlib/seaborn for plotting
- Assume the DataFrame variable is named 'df'
- Include plt.show() to display plots
- Focus on visualizations that reveal insights about this specific data

Generate visualization code based on the DataFrame structure and sample data provided."""

ML_PROMPT = """You are a machine learning expert. Generate Python code to train a machine learning model on the provided DataFrame.

Requirements:
- Return ONLY executable Python code, no explanations
- Add inline comments explaining each step
- Handle preprocessing, splitting, training, and evaluation
- Use scikit-learn for modeling
- Assume the DataFrame variable is named 'df' and target column is provided
- Store the trained model in a variable called 'model'
- Include model evaluation metrics

Generate complete ML pipeline code based on the DataFrame structure and target column."""

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
        
    # Save the key
    config = load_config()
    config['gemini_api_key'] = api_key
    save_config(config)
    
    print("✅ API key saved successfully!")
    return api_key

def get_gemini_api_key():
    """Get Gemini API key with simple setup."""
    # Try environment variable first
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    # Try saved configuration
    config = load_config()
    api_key = config.get('gemini_api_key')
    if api_key:
        return api_key
    
    # Simple setup
    print("\n⚠️  No API key found. Let's set one up!")
    return setup_api_key()

def call_gemini_api(system_prompt: str, user_prompt: str, model: str = "gemini-1.5-flash") -> str:
    """
    Call Google Gemini API with bulletproof response parsing.
    
    Args:
        system_prompt: System prompt for AI
        user_prompt: User prompt
        model: Model to use (default: gemini-1.5-flash)
        
    Returns:
        str: AI response
    """
    try:
        api_key = get_gemini_api_key()
        
        # Use the correct model name format
        model_map = {
            "gemini-2.5-flash": "gemini-1.5-flash",  # Map to stable version
            "gemini-2.5-pro": "gemini-1.5-pro",
            "gemini-2.0-flash-exp": "gemini-1.5-flash",
            "gemini-1.5-flash": "gemini-1.5-flash",
            "gemini-1.5-pro": "gemini-1.5-pro"
        }
        
        actual_model = model_map.get(model, "gemini-1.5-flash")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{actual_model}:generateContent"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Combine prompts
        full_prompt = f"{system_prompt}\n\nUser Request: {user_prompt}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
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
        
        # Extract text from the response
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                parts = candidate['content']['parts']
                if len(parts) > 0 and 'text' in parts[0]:
                    text = parts[0]['text'].strip()
                    
                    # Clean up common markdown artifacts
                    text = text.replace('```python', '').replace('```', '')
                    text = text.strip()
                    
                    return text
        
        # Fallback extraction
        def extract_any_text(obj, depth=0):
            """Recursively extract text from any nested structure."""
            if depth > 10:  # Prevent infinite recursion
                return None
            
            if isinstance(obj, str) and len(obj) > 10:
                return obj.strip()
            elif isinstance(obj, dict):
                # Priority keys
                for key in ['text', 'output', 'content', 'response']:
                    if key in obj and isinstance(obj[key], str) and len(obj[key]) > 10:
                        return obj[key].strip()
                # Try all other keys
                for key, value in obj.items():
                    result_text = extract_any_text(value, depth + 1)
                    if result_text:
                        return result_text
            elif isinstance(obj, list):
                for item in obj:
                    result_text = extract_any_text(item, depth + 1)
                    if result_text:
                        return result_text
            return None
        
        text = extract_any_text(result)
        if text:
            # Clean up markdown
            text = text.replace('```python', '').replace('```', '').strip()
            return text
        
        raise Exception(f"No text content found in API response. Response structure: {json.dumps(result, indent=2)[:500]}...")
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error calling Gemini API: {str(e)}")
    except Exception as e:
        if "API key not valid" in str(e):
            print("\n❌ Invalid API key. Please run: keeya.setup()")
        raise Exception(f"Failed to call Gemini API: {str(e)}")

def call_ai_api(system_prompt: str, user_prompt: str, model: str = "gemini-1.5-flash") -> str:
    """
    Call Gemini AI API.
    
    Args:
        system_prompt: System prompt for AI
        user_prompt: User prompt
        model: Model to use (default: gemini-1.5-flash)
        
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
            sample_data[col] = [
                str(val) if not isinstance(val, (str, int, float, bool)) else val 
                for val in sample_values
            ]
        except Exception:
            # If conversion fails, use string representation
            sample_data[col] = [str(val) for val in df[col].dropna().head(3)]
    
    # Calculate missing values
    missing_dict = {}
    for col in df.columns:
        missing_dict[col] = int(df[col].isnull().sum())
    
    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": dtypes_dict,
        "missing_values": missing_dict,
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
    
    # Import common libraries
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Safe globals with common imports
    safe_globals = {
        "__builtins__": __builtins__,
        "pd": pd,
        "np": np,
        "plt": plt,
        "sns": sns,
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
        "isinstance": isinstance
    }
    
    # Add context variables
    safe_globals.update(context)
    
    try:
        # Execute the code
        exec(code, safe_globals)
        
        # Try to find result variables
        result_vars = ['analysis_results', 'result', 'output', 'cleaned_df', 'model', 'cleaned_data']
        for var in result_vars:
            if var in safe_globals:
                return safe_globals[var]
        
        return None
        
    except Exception as e:
        raise Exception(f"Failed to execute code: {str(e)}")

def is_valid_python_code(code: str) -> bool:
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
    
    # Just model names or error messages (common invalid responses)
    invalid_responses = [
        "gemini-2.5-flash", 
        "gemini-2.5-pro", 
        "gemini-1.5-flash",
        "gemini-2.0-flash-exp",
        "I cannot", 
        "I'm sorry",
        "I apologize"
    ]
    
    for invalid in invalid_responses:
        if invalid.lower() in code.lower()[:100]:  # Check beginning of response
            return False
    
    # Must contain some Python-like elements
    python_indicators = ['=', 'def ', 'import ', 'for ', 'if ', 'class ', '#', 'print(', '.', '[', ']', '(', ')']
    indicators_found = sum(1 for indicator in python_indicators if indicator in code)
    
    if indicators_found < 3:  # Need at least 3 Python indicators
        return False
    
    return True

def get_available_models() -> Dict[str, str]:
    """
    Get available models with their descriptions.
    
    Returns:
        Dict: Model names and descriptions
    """
    return {
        "gemini-1.5-flash": "Gemini 1.5 Flash (Fast, reliable, free tier available)",
        "gemini-1.5-pro": "Gemini 1.5 Pro (Most capable, better quality)",
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
        "import pandas as pd",
        "import numpy as np",
        "",
        "# Create a copy to avoid modifying original DataFrame",
        "cleaned_df = df.copy()",
        "",
        "# Remove duplicate rows",
        "initial_shape = cleaned_df.shape",
        "cleaned_df = cleaned_df.drop_duplicates()",
        "print(f'Removed {initial_shape[0] - cleaned_df.shape[0]} duplicate rows')",
        ""
    ]
    
    # Handle missing values based on data types
    numeric_cols = [col for col, dtype in df_info['dtypes'].items() if 'int' in dtype or 'float' in dtype]
    object_cols = [col for col, dtype in df_info['dtypes'].items() if 'object' in dtype or 'string' in dtype]
    
    if numeric_cols:
        code_lines.extend([
            "# Fill missing values in numeric columns with median",
            f"numeric_cols = {numeric_cols}",
            "for col in numeric_cols:",
            "    if col in cleaned_df.columns:",
            "        median_val = cleaned_df[col].median()",
            "        if pd.notna(median_val):",
            "            cleaned_df[col] = cleaned_df[col].fillna(median_val)",
            ""
        ])
    
    if object_cols:
        code_lines.extend([
            "# Fill missing values in text columns with 'Unknown'",
            f"text_cols = {object_cols}",
            "for col in text_cols:",
            "    if col in cleaned_df.columns:",
            "        cleaned_df[col] = cleaned_df[col].fillna('Unknown')",
            "        # Convert to string, lowercase and strip whitespace",
            "        cleaned_df[col] = cleaned_df[col].astype(str).str.lower().str.strip()",
            ""
        ])
    
    # Add specific cleaning based on missing values
    missing_values = df_info.get('missing_values', {})
    high_missing_cols = [col for col, count in missing_values.items() if count > len(df) * 0.5]
    
    if high_missing_cols:
        code_lines.extend([
            "# Columns with >50% missing values (consider dropping):",
            f"# High missing columns: {high_missing_cols}",
            "# Uncomment the next line if you want to drop them:",
            f"# cleaned_df = cleaned_df.drop(columns={high_missing_cols})",
            ""
        ])
    
    code_lines.extend([
        "# Reset index",
        "cleaned_df = cleaned_df.reset_index(drop=True)",
        "",
        "# Display cleaning summary",
        "print('\\n' + '='*50)",
        "print('CLEANING SUMMARY')",
        "print('='*50)",
        f"print(f'Original shape: {df.shape}')",
        "print(f'Cleaned shape: {cleaned_df.shape}')",
        "print(f'Rows removed: {df.shape[0] - cleaned_df.shape[0]}')",
        "print(f'Missing values remaining: {cleaned_df.isnull().sum().sum()}')",
        "",
        "# Display the cleaned DataFrame",
        "print('\\nFirst 5 rows of cleaned DataFrame:')",
        "print(cleaned_df.head())",
        "",
        "# Store result",
        "result = cleaned_df"
    ])
    
    return "\n".join(code_lines)

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
        "import numpy as np",
        "",
        "# Set style for better plots",
        "plt.style.use('seaborn-v0_8-darkgrid')",
        "sns.set_palette('husl')",
        ""
    ]
    
    # Get column types
    numeric_cols = [col for col, dtype in df_info['dtypes'].items() if 'int' in dtype or 'float' in dtype]
    object_cols = [col for col, dtype in df_info['dtypes'].items() if 'object' in dtype or 'string' in dtype]
    
    plot_count = 0
    
    # Generate plots based on data types and plot_type parameter
    if plot_type and plot_type.lower() == "correlation" and len(numeric_cols) >= 2:
        code_lines.extend([
            "# Correlation heatmap",
            "plt.figure(figsize=(10, 8))",
            f"numeric_cols = {numeric_cols}",
            "correlation_matrix = df[numeric_cols].corr()",
            "sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')",
            "plt.title('Correlation Matrix of Numeric Variables', fontsize=14, fontweight='bold')",
            "plt.tight_layout()",
            "plt.show()",
            ""
        ])
        plot_count += 1
    
    # Default visualizations if no specific type requested
    if not plot_type or plot_type.lower() in ["distribution", "histogram"]:
        if numeric_cols:
            # Distribution plots for first few numeric columns
            for i, col in enumerate(numeric_cols[:min(2, len(numeric_cols))]):
                code_lines.extend([
                    f"# Distribution plot for {col}",
                    "plt.figure(figsize=(10, 6))",
                    f"plt.hist(df['{col}'].dropna(), bins=30, alpha=0.7, edgecolor='black', color='skyblue')",
                    f"plt.axvline(df['{col}'].mean(), color='red', linestyle='--', label='Mean')",
                    f"plt.axvline(df['{col}'].median(), color='green', linestyle='--', label='Median')",
                    f"plt.title('Distribution of {col}', fontsize=14, fontweight='bold')",
                    f"plt.xlabel('{col}')",
                    "plt.ylabel('Frequency')",
                    "plt.legend()",
                    "plt.grid(True, alpha=0.3)",
                    "plt.tight_layout()",
                    "plt.show()",
                    ""
                ])
                plot_count += 1
                if plot_count >= 3:
                    break
    
    if (not plot_type or plot_type.lower() in ["bar", "categorical"]) and plot_count < 3:
        if object_cols:
            # Bar plots for categorical columns
            for i, col in enumerate(object_cols[:min(1, len(object_cols))]):
                code_lines.extend([
                    f"# Bar plot for {col}",
                    "plt.figure(figsize=(12, 6))",
                    f"value_counts = df['{col}'].value_counts().head(10)",
                    "colors = plt.cm.viridis(np.linspace(0, 1, len(value_counts)))",
                    "bars = plt.bar(range(len(value_counts)), value_counts.values, color=colors)",
                    "plt.xticks(range(len(value_counts)), value_counts.index, rotation=45, ha='right')",
                    f"plt.title('Top 10 Values in {col}', fontsize=14, fontweight='bold')",
                    f"plt.xlabel('{col}')",
                    "plt.ylabel('Count')",
                    "# Add value labels on bars",
                    "for bar in bars:",
                    "    height = bar.get_height()",
                    "    plt.text(bar.get_x() + bar.get_width()/2., height,",
                    "             f'{int(height)}', ha='center', va='bottom')",
                    "plt.tight_layout()",
                    "plt.show()",
                    ""
                ])
                plot_count += 1
    
    # Scatter plot if we have at least 2 numeric columns and haven't reached limit
    if (not plot_type or plot_type.lower() in ["scatter", "relationship"]) and len(numeric_cols) >= 2 and plot_count < 3:
        col1, col2 = numeric_cols[0], numeric_cols[1]
        code_lines.extend([
            f"# Scatter plot: {col1} vs {col2}",
            "plt.figure(figsize=(10, 6))",
            f"plt.scatter(df['{col1}'], df['{col2}'], alpha=0.6, s=50, c='purple')",
            f"plt.xlabel('{col1}', fontsize=12)",
            f"plt.ylabel('{col2}', fontsize=12)",
            f"plt.title('{col1} vs {col2}', fontsize=14, fontweight='bold')",
            "plt.grid(True, alpha=0.3)",
            "plt.tight_layout()",
            "plt.show()",
            ""
        ])
        plot_count += 1
    
    # Missing values visualization if relevant
    missing_values = df_info.get('missing_values', {})
    cols_with_missing = {col: count for col, count in missing_values.items() if count > 0}
    
    if cols_with_missing and plot_count < 3:
        code_lines.extend([
            "# Missing values visualization",
            "plt.figure(figsize=(12, 6))",
            f"missing_data = {cols_with_missing}",
            "cols = list(missing_data.keys())",
            "counts = list(missing_data.values())",
            "colors = ['red' if c > len(df)*0.1 else 'orange' for c in counts]",
            "bars = plt.bar(range(len(cols)), counts, color=colors)",
            "plt.xticks(range(len(cols)), cols, rotation=45, ha='right')",
            "plt.title('Missing Values by Column', fontsize=14, fontweight='bold')",
            "plt.xlabel('Columns')",
            "plt.ylabel('Missing Count')",
            "# Add percentage labels",
            "for i, (bar, count) in enumerate(zip(bars, counts)):",
            "    pct = (count / len(df)) * 100",
            "    plt.text(bar.get_x() + bar.get_width()/2., count,",
            "             f'{pct:.1f}%', ha='center', va='bottom')",
            "plt.tight_layout()",
            "plt.show()",
            ""
        ])
    
    code_lines.extend([
        "",
        "# Display basic DataFrame statistics",
        "print('\\n' + '='*50)",
        "print('DATAFRAME STATISTICS')",
        "print('='*50)",
        f"print('Shape: {df_info['shape']}')",
        f"print('Columns ({len(df_info['columns'])}): {', '.join(df_info['columns'][:5])}...' if len(df_info['columns']) > 5 else ', '.join(df_info['columns']))",
        "print('\\nNumeric columns summary:')",
        "print(df.describe())",
        "",
        f"# Total of {plot_count} visualizations created"
    ])
    
    return "\n".join(code_lines)

# Main API Functions
def generate(prompt: str, model: str = "gemini-1.5-flash") -> str:
    """
    Generate Python code from natural language prompt.

    Args:
        prompt: Natural language description of what you want to generate
        model: Model to use (default: gemini-1.5-flash)

    Returns:
        str: Generated Python code
    """
    try:
        print(f"\n🤖 Generating code with {model}...")
        response = call_ai_api(
            system_prompt=GENERATE_PROMPT,
            user_prompt=prompt,
            model=model
        )
        
        if is_valid_python_code(response):
            print("✨ AI Generated Code:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            print("📋 Copy and run this code!")
            return response
        else:
            raise Exception("AI returned invalid response")
            
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg:
            print("\n❌ API key issue. Please run: keeya.setup()")
        else:
            print(f"\n❌ Generation failed: {error_msg}")
        raise

def clean(df: pd.DataFrame, model: str = "gemini-1.5-flash") -> str:
    """
    Generate code to clean a DataFrame using AI with fallback.

    Args:
        df: DataFrame to clean
        model: Model to use (default: gemini-1.5-flash)

    Returns:
        str: Generated Python code for cleaning the DataFrame
    """
    try:
        print(f"\n🧹 Generating cleaning code with {model}...")
        
        # Analyze DataFrame
        df_info = analyze_dataframe(df)
        
        # Create user prompt with DataFrame info
        user_prompt = f"""Clean this DataFrame:

DataFrame Info:
{json.dumps(df_info, indent=2)}

Sample Data:
{df.head().to_string()}

Generate Python code to clean this DataFrame effectively."""
        
        # Call AI API
        response = call_ai_api(
            system_prompt=CLEAN_PROMPT,
            user_prompt=user_prompt,
            model=model
        )
        
        # Validate the response is actually Python code
        if not is_valid_python_code(response):
            raise Exception(f"AI returned invalid code - using fallback")
            
        print("✨ AI Generated Cleaning Code:")
        print("=" * 50)
        print(response)
        print("=" * 50)
        print("📋 Copy and run this code to clean your DataFrame!")
        
        return response
            
    except Exception as e:
        # Fallback: Generate basic cleaning code
        print("⚠️  AI generation failed. Using fallback cleaning code...")
        print(f"   Error: {str(e)[:100]}")
        print()
        
        fallback_code = generate_fallback_cleaning_code(df)
        
        print("🧹 Fallback Cleaning Code:")
        print("=" * 50)
        print(fallback_code)
        print("=" * 50)
        print("📋 Copy and run this basic cleaning code!")
        
        return fallback_code

def analyze(df: pd.DataFrame, model: str = "gemini-1.5-flash") -> dict:
    """
    Analyze a DataFrame using AI.

    Args:
        df: DataFrame to analyze
        model: Model to use (default: gemini-1.5-flash)

    Returns:
        dict: Analysis results with formatted output
    """
    try:
        print(f"\n📊 Analyzing DataFrame with {model}...")
        
        # Analyze DataFrame
        df_info = analyze_dataframe(df)
        
        # Create user prompt with DataFrame info
        user_prompt = f"""Analyze this DataFrame:

DataFrame Info:
{json.dumps(df_info, indent=2)}

Sample Data:
{df.head().to_string()}

Generate comprehensive analysis code that stores results in 'analysis_results' dictionary."""
        
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
            print("\n📊 DataFrame Analysis Results:")
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
                    elif isinstance(value, pd.DataFrame):
                        print(value.to_string())
                    else:
                        print(f"  {value}")
            else:
                print(result)
            
            print("=" * 60)
            return result
        else:
            # Fallback: Basic analysis
            print("⚠️  Using basic analysis fallback...")
            analysis_results = {
                "shape": df.shape,
                "columns": list(df.columns),
                "missing_values": df.isnull().sum().to_dict(),
                "numeric_summary": df.describe().to_dict() if not df.select_dtypes(include=[np.number]).empty else {},
                "data_types": df.dtypes.astype(str).to_dict()
            }
            
            print("\n📊 Basic Analysis Results:")
            print("=" * 60)
            for key, value in analysis_results.items():
                print(f"\n{key.replace('_', ' ').title()}:")
                print(value)
            print("=" * 60)
            
            return analysis_results
            
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        # Return basic analysis as fallback
        return {
            "error": str(e),
            "shape": df.shape,
            "columns": list(df.columns)
        }

def visualize(df: pd.DataFrame, plot_type: Optional[str] = None, model: str = "gemini-1.5-flash") -> str:
    """
    Generate visualization code for a DataFrame using AI with fallback.

    Args:
        df: DataFrame to visualize
        plot_type: Type of plot to create (optional)
        model: Model to use (default: gemini-1.5-flash)

    Returns:
        str: Generated Python code for visualizations
    """
    try:
        print(f"\n📈 Generating visualization code with {model}...")
        
        # Analyze DataFrame
        df_info = analyze_dataframe(df)
        
        # Create user prompt with DataFrame info
        user_prompt = f"""Create visualizations for this DataFrame:

DataFrame Info:
{json.dumps(df_info, indent=2)}

Sample Data:
{df.head().to_string()}"""
        
        if plot_type:
            user_prompt += f"\n\nPreferred plot type: {plot_type}"
        
        user_prompt += "\n\nGenerate Python code for meaningful visualizations."
        
        # Call AI API
        response = call_ai_api(
            system_prompt=VISUALIZE_PROMPT,
            user_prompt=user_prompt,
            model=model
        )
        
        # Validate the response is actually Python code
        if not is_valid_python_code(response):
            raise Exception(f"AI returned invalid code - using fallback")
            
        print("✨ AI Generated Visualization Code:")
        print("=" * 50)
        print(response)
        print("=" * 50)
        print("📋 Copy and run this code to create visualizations!")
        
        return response
        
    except Exception as e:
        # Fallback: Generate basic visualization code
        print("⚠️  AI generation failed. Using fallback visualization code...")
        print(f"   Error: {str(e)[:100]}")
        print()
        
        fallback_code = generate_fallback_visualization_code(df, plot_type)
        
        print("📈 Fallback Visualization Code:")
        print("=" * 50)
        print(fallback_code)
        print("=" * 50)
        print("📋 Copy and run this basic visualization code!")
        
        return fallback_code

def train(df: pd.DataFrame, target: str, model: str = "gemini-1.5-flash") -> str:
    """
    Generate machine learning code for a DataFrame using AI.

    Args:
        df: DataFrame with training data
        target: Target column name
        model: Model to use (default: gemini-1.5-flash)

    Returns:
        str: Generated machine learning pipeline code
    """
    try:
        print(f"\n🤖 Generating ML pipeline code with {model}...")
        
        # Check if target column exists
        if target not in df.columns:
            raise ValueError(f"Target column '{target}' not found in DataFrame. Available columns: {list(df.columns)}")
        
        # Analyze DataFrame
        df_info = analyze_dataframe(df)
        
        # Determine task type
        target_dtype = str(df[target].dtype)
        unique_values = df[target].nunique()
        task_type = "regression" if 'float' in target_dtype or 'int' in target_dtype and unique_values > 10 else "classification"
        
        # Create user prompt with DataFrame info
        user_prompt = f"""Create a machine learning pipeline for this DataFrame:

DataFrame Info:
{json.dumps(df_info, indent=2)}

Target Column: {target}
Task Type: {task_type}
Target Unique Values: {unique_values}

Sample Data:
{df.head().to_string()}

Generate complete ML pipeline code including preprocessing, training, and evaluation."""
        
        # Call AI API
        response = call_ai_api(
            system_prompt=ML_PROMPT,
            user_prompt=user_prompt,
            model=model
        )
        
        # Validate the response is actually Python code
        if not is_valid_python_code(response):
            # Generate fallback ML code
            raise Exception("AI returned invalid code - using fallback")
            
        print("✨ AI Generated ML Pipeline Code:")
        print("=" * 50)
        print(response)
        print("=" * 50)
        print("📋 Copy and run this code to train your model!")
        
        return response
        
    except Exception as e:
        # Fallback: Generate basic ML code
        print("⚠️  AI generation failed. Using fallback ML code...")
        print(f"   Error: {str(e)[:100]}")
        print()
        
        fallback_code = generate_fallback_ml_code(df, target)
        
        print("🤖 Fallback ML Pipeline Code:")
        print("=" * 50)
        print(fallback_code)
        print("=" * 50)
        print("📋 Copy and run this basic ML pipeline code!")
        
        return fallback_code

def generate_fallback_ml_code(df: pd.DataFrame, target: str) -> str:
    """
    Generate basic fallback ML code when AI fails.
    
    Args:
        df: DataFrame with training data
        target: Target column name
        
    Returns:
        str: Basic Python code for ML pipeline
    """
    df_info = analyze_dataframe(df)
    
    # Determine task type
    target_dtype = str(df[target].dtype)
    unique_values = df[target].nunique()
    is_classification = 'object' in target_dtype or (unique_values <= 10 and unique_values > 1)
    
    code_lines = [
        "# Basic Machine Learning Pipeline",
        "import pandas as pd",
        "import numpy as np",
        "from sklearn.model_selection import train_test_split",
        "from sklearn.preprocessing import StandardScaler, LabelEncoder",
        "from sklearn.impute import SimpleImputer",
    ]
    
    if is_classification:
        code_lines.extend([
            "from sklearn.ensemble import RandomForestClassifier",
            "from sklearn.metrics import accuracy_score, classification_report, confusion_matrix"
        ])
    else:
        code_lines.extend([
            "from sklearn.ensemble import RandomForestRegressor",
            "from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error"
        ])
    
    code_lines.extend([
        "",
        "# Prepare the data",
        "df_ml = df.copy()",
        "",
        "# Separate features and target",
        f"target_column = '{target}'",
        "X = df_ml.drop(columns=[target_column])",
        "y = df_ml[target_column]",
        "",
        "# Handle missing values in target",
        "mask = y.notna()",
        "X = X[mask]",
        "y = y[mask]",
        "",
        "# Identify numeric and categorical columns",
        "numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()",
        "categorical_features = X.select_dtypes(include=['object', 'string']).columns.tolist()",
        "",
        "print(f'Numeric features: {numeric_features}')",
        "print(f'Categorical features: {categorical_features}')",
        "",
        "# Handle numeric features",
        "if numeric_features:",
        "    imputer_num = SimpleImputer(strategy='median')",
        "    X[numeric_features] = imputer_num.fit_transform(X[numeric_features])",
        "",
        "# Handle categorical features",
        "if categorical_features:",
        "    # Fill missing values",
        "    imputer_cat = SimpleImputer(strategy='constant', fill_value='missing')",
        "    X[categorical_features] = imputer_cat.fit_transform(X[categorical_features])",
        "    ",
        "    # Encode categorical variables",
        "    for col in categorical_features:",
        "        le = LabelEncoder()",
        "        X[col] = le.fit_transform(X[col].astype(str))",
        "",
        "# Split the data",
        "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)",
        "",
        "# Scale features",
        "scaler = StandardScaler()",
        "X_train_scaled = scaler.fit_transform(X_train)",
        "X_test_scaled = scaler.transform(X_test)",
        ""
    ])
    
    if is_classification:
        code_lines.extend([
            "# Train Random Forest Classifier",
            "model = RandomForestClassifier(n_estimators=100, random_state=42)",
            "model.fit(X_train_scaled, y_train)",
            "",
            "# Make predictions",
            "y_pred = model.predict(X_test_scaled)",
            "",
            "# Evaluate the model",
            "accuracy = accuracy_score(y_test, y_pred)",
            "print('\\n' + '='*50)",
            "print('MODEL EVALUATION RESULTS')",
            "print('='*50)",
            "print(f'Accuracy: {accuracy:.4f}')",
            "print('\\nClassification Report:')",
            "print(classification_report(y_test, y_pred))",
            "print('\\nConfusion Matrix:')",
            "print(confusion_matrix(y_test, y_pred))",
        ])
    else:
        code_lines.extend([
            "# Train Random Forest Regressor",
            "model = RandomForestRegressor(n_estimators=100, random_state=42)",
            "model.fit(X_train_scaled, y_train)",
            "",
            "# Make predictions",
            "y_pred = model.predict(X_test_scaled)",
            "",
            "# Evaluate the model",
            "mse = mean_squared_error(y_test, y_pred)",
            "mae = mean_absolute_error(y_test, y_pred)",
            "r2 = r2_score(y_test, y_pred)",
            "rmse = np.sqrt(mse)",
            "",
            "print('\\n' + '='*50)",
            "print('MODEL EVALUATION RESULTS')",
            "print('='*50)",
            "print(f'R² Score: {r2:.4f}')",
            "print(f'RMSE: {rmse:.4f}')",
            "print(f'MAE: {mae:.4f}')",
            "print(f'MSE: {mse:.4f}')",
        ])
    
    code_lines.extend([
        "",
        "# Feature importance",
        "feature_importance = pd.DataFrame({",
        "    'feature': X.columns,",
        "    'importance': model.feature_importances_",
        "}).sort_values('importance', ascending=False)",
        "",
        "print('\\nTop 10 Most Important Features:')",
        "print(feature_importance.head(10))",
        "",
        "# Store the trained model",
        "print('\\nModel trained successfully!')",
        "print(f'Training set size: {len(X_train)}')",
        "print(f'Test set size: {len(X_test)}')"
    ])
    
    return "\n".join(code_lines)

def reset_api_key():
    """Reset/change the API key."""
    config = load_config()
    if 'gemini_api_key' in config:
        del config['gemini_api_key']
        save_config(config)
        print("✅ API key has been reset")

def setup():
    """Set up or change your Gemini API key."""
    print("\n🚀 Welcome to Keeya Setup!")
    print("=" * 40)
    
    # Check if key already exists
    config = load_config()
    if 'gemini_api_key' in config:
        print("ℹ️  An API key is already configured.")
        choice = input("Do you want to replace it? (y/n): ")
        if choice.lower() != 'y':
            print("Setup cancelled.")
            return
        reset_api_key()
    
    try:
        setup_api_key()
        print("\n✅ Setup complete! You can now use Keeya functions:")
        print("  • keeya.generate('your prompt')")
        print("  • keeya.clean(df)")
        print("  • keeya.analyze(df)")
        print("  • keeya.visualize(df)")
        print("  • keeya.train(df, 'target_column')")
        print("\nEnjoy using Keeya! 🎉")
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")

def test_connection():
    """Test if the API key is working."""
    try:
        print("\n🔍 Testing Gemini API connection...")
        response = call_ai_api(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say 'Hello from Keeya!' in exactly 3 words.",
            model="gemini-1.5-flash"
        )
        print(f"✅ Connection successful! Response: {response}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

# Add a help function
def help():
    """Display help information about Keeya functions."""
    print("\n" + "="*60)
    print("KEEYA - AI-Powered Data Analysis Tool")
    print("="*60)
    print("\n📚 Available Functions:\n")
    
    functions = [
        ("setup()", "Configure your Gemini API key"),
        ("generate(prompt)", "Generate Python code from natural language"),
        ("clean(df)", "Generate DataFrame cleaning code"),
        ("analyze(df)", "Analyze a DataFrame"),
        ("visualize(df, plot_type=None)", "Generate visualization code"),
        ("train(df, target)", "Generate ML pipeline code"),
        ("test_connection()", "Test API connection"),
        ("reset_api_key()", "Reset your API key"),
        ("get_available_models()", "List available models"),
        ("help()", "Show this help message")
    ]
    
    for func, desc in functions:
        print(f"  {func:<30} - {desc}")
    
    print("\n📖 Examples:\n")
    print("  import keeya")
    print("  import pandas as pd")
    print()
    print("  # Setup API key")
    print("  keeya.setup()")
    print()
    print("  # Generate code")
    print("  code = keeya.generate('create a function to calculate fibonacci')")
    print()
    print("  # Clean a DataFrame")
    print("  df = pd.read_csv('data.csv')")
    print("  cleaning_code = keeya.clean(df)")
    print()
    print("  # Analyze data")
    print("  results = keeya.analyze(df)")
    print()
    print("  # Create visualizations")
    print("  viz_code = keeya.visualize(df, plot_type='correlation')")
    print()
    print("  # Train ML model")
    print("  ml_code = keeya.train(df, 'target_column')")
    print()
    print("🔗 Get your free API key at:")
    print("   https://aistudio.google.com/app/apikey")
    print("="*60)

# Print welcome message when imported
print("🎉 Keeya loaded successfully!")
print("Run keeya.help() for usage information or keeya.setup() to configure.")