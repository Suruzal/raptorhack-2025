def validate_input(data):
    # Validate user input data
    if not isinstance(data, dict):
        raise ValueError("Input data must be a dictionary.")
    required_fields = ['name', 'classes', 'grades', 'APs', 'current_classes', 'strengths', 'weaknesses', 'portfolio', 'major']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

def format_markdown(text):
    # Format text for Markdown
    return text.strip().replace('\n', '\n\n')

def extract_portfolio_images(portfolio):
    # Extract image URLs from the portfolio
    return [item['image_url'] for item in portfolio if 'image_url' in item]