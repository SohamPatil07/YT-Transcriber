# YouTube Transcript to Detailed Notes Converter

This application converts YouTube video transcripts into detailed notes using AI-powered summarization. It provides summaries in multiple languages and allows users to compare summaries of different lengths.

## Features

- Extract transcripts from YouTube videos
- Generate summaries in multiple languages
- Create summaries of varying lengths (Brief, Detailed, Comprehensive)
- Download summaries as PDF files
- Compare summaries of different lengths

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.9 or higher
- pip (Python package manager)
- A Google API key for the Gemini Pro model

## Installation

1. Clone the repository:   ```
   git clone https://github.com/your-username/youtube-transcript-summarizer.git
   cd youtube-transcript-summarizer   ```

2. Create a virtual environment (optional but recommended):   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`   ```

3. Install the required packages:   ```
   pip install -r requirements.txt   ```

4. Create a `.env` file in the project root directory and add your Google API key:   ```
   GOOGLE_API_KEY=your_api_key_here   ```

## Usage

1. Run the Streamlit app:   ```
   streamlit run app.py   ```

2. Open your web browser and go to `http://localhost:8501`

3. Enter a YouTube video URL, select the desired language and summary length, and click "Get Detailed Notes"

4. View the generated summary and download it as a PDF if desired

## Docker Support

To run the application using Docker:

1. Build the Docker image:   ```
   docker build -t youtube-summary-app .   ```

2. Run the Docker container:   ```
   docker run -p 8501:8501 -e GOOGLE_API_KEY=your_api_key_here youtube-summary-app   ```

3. Access the application at `http://localhost:8501`

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## License

This project is currently not licensed. All rights are reserved by the project owner. For more information about choosing a license, visit [choosealicense.com](https://choosealicense.com/).

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the web application framework
- [Google Generative AI](https://cloud.google.com/ai-platform/training/docs/algorithms/generative-ai) for the summarization model
- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api) for transcript extraction
