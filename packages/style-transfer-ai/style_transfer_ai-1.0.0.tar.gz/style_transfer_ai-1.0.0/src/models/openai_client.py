"""
OpenAI client for cloud-based AI analysis.
Handles API key management and text analysis requests.
"""

from ..config.settings import OPENAI_API_KEY


def get_api_key(existing_key=None):
    """Get OpenAI API key from user with validation."""
    existing_key = existing_key or OPENAI_API_KEY
    
    # Check if there's an existing API key
    if existing_key and len(existing_key) > 20:
        masked_key = f"{existing_key[:10]}...{existing_key[-10:]}"
        print(f"\nFound existing OpenAI API key: {masked_key}")
        use_existing = input("Do you want to use this OpenAI API key? (y/n): ").strip().lower()
        
        if use_existing == 'y':
            return existing_key
    
    # Get new API key from user
    print("\nPlease enter your OpenAI API key:")
    print("(You can find this at: https://platform.openai.com/api-keys)")
    
    while True:
        try:
            api_key = input("API Key: ").strip()
            
            if not api_key:
                print("API key cannot be empty. Please try again.")
                continue
                
            if len(api_key) < 20:
                print("API key seems too short. Please check and try again.")
                continue
                
            return api_key
            
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user.")
            return None


def setup_openai_client(api_key=None):
    """Initialize OpenAI client with provided API key."""
    try:
        from openai import OpenAI
        
        # Use provided key or get from user
        if not api_key:
            api_key = get_api_key()
        
        if not api_key:
            return None, "No API key provided"
        
        client = OpenAI(api_key=api_key)
        return client, f"OpenAI client initialized successfully with key: {api_key[:10]}...{api_key[-10:]}"
    except ImportError:
        return None, "OpenAI library not installed. Run: pip install openai"
    except Exception as e:
        return None, f"Error initializing OpenAI client: {e}"


def analyze_with_openai(client, prompt):
    """
    Perform analysis using OpenAI API.
    
    Args:
        client: Initialized OpenAI client
        prompt (str): The analysis prompt
        
    Returns:
        str: Analysis result or error message
    """
    if not client:
        return "OpenAI Error: No client provided. Please ensure client is initialized."
    
    print("Sending request to OpenAI GPT-3.5-turbo model...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Lower for more consistent analysis
            max_tokens=3000   # More tokens for deep analysis
        )
        
        print("Deep analysis completed successfully!")
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI API Error: {e}"