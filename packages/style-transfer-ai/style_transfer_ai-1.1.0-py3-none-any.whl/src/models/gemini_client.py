"""
Google Gemini client for cloud-based AI analysis.
Handles API key management and text analysis requests.
"""

from ..config.settings import GEMINI_API_KEY


def get_api_key(existing_key=None):
    """Get Gemini API key from user with validation."""
    existing_key = existing_key or GEMINI_API_KEY
    
    # Check if there's an existing API key
    if existing_key and len(existing_key) > 20:
        masked_key = f"{existing_key[:10]}...{existing_key[-10:]}"
        print(f"\nFound existing Google Gemini API key: {masked_key}")
        use_existing = input("Do you want to use this Gemini API key? (y/n): ").strip().lower()
        
        if use_existing == 'y':
            return existing_key
    
    # Get new API key from user
    print("\nPlease enter your Google Gemini API key:")
    print("(You can find this at: https://aistudio.google.com/app/apikey)")
    
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


def setup_gemini_client(api_key=None):
    """Initialize Gemini client with provided API key."""
    try:
        import google.generativeai as genai
        
        # Use provided key or get from user
        if not api_key:
            api_key = get_api_key()
        
        if not api_key:
            return None, "No API key provided"
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Create the model instance
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        return model, f"Gemini client initialized successfully with key: {api_key[:10]}...{api_key[-10:]}"
    except ImportError:
        return None, "Google Generative AI library not installed. Run: pip install google-generativeai"
    except Exception as e:
        return None, f"Error initializing Gemini client: {e}"


def analyze_with_gemini(client, prompt):
    """
    Perform analysis using Gemini API.
    
    Args:
        client: Initialized Gemini client
        prompt (str): The analysis prompt
        
    Returns:
        str: Analysis result or error message
    """
    if not client:
        return "Gemini Error: No client provided. Please ensure client is initialized."
    
    print("Sending request to Google Gemini-1.5-flash model...")
    
    try:
        # Import for generation config
        import google.generativeai as genai
        
        # Configure generation settings for consistent analysis
        generation_config = genai.types.GenerationConfig(
            temperature=0.2,
            max_output_tokens=3000,
            candidate_count=1
        )
        
        response = client.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        print("Deep analysis completed successfully!")
        return response.text
    except Exception as e:
        return f"Gemini API Error: {e}"