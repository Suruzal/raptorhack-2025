# User Matching App

This project is designed to help students find potential study partners based on shared classes and complementary strengths and weaknesses. It allows users to input their academic information, including classes, grades, AP scores, current classes, strengths and weaknesses, and a portfolio in Markdown format.

## Features

- User registration and data entry
- Database storage using SQLite
- Gemini API integration for matching users
- Portfolio creation with images and Markdown text
- Strengths and weaknesses analysis for better matching

## Project Structure

```
user-matching-app
├── src
│   ├── main.py                # Entry point of the application
│   ├── database
│   │   ├── connection.py      # Database connection handling
│   │   └── models.py          # Data models for user entries
│   ├── api
│   │   └── gemini_api.py      # Gemini API integration
│   ├── services
│   │   ├── user_service.py     # User management services
│   │   └── matching_service.py  # Study partner matching services
│   ├── utils
│   │   └── helpers.py          # Utility functions
│   └── templates
│       └── portfolio_template.md # Portfolio template
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
└── .env                        # Environment variables
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd user-matching-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure your environment variables in the `.env` file.

4. Run the application:
   ```
   python src/main.py
   ```

## Usage Guidelines

- Users can register and input their academic information through the user interface.
- The application will store user data in the SQLite database.
- Users can view potential study partners based on their classes and strengths/weaknesses.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.