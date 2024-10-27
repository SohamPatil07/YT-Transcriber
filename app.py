import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
import io
from reportlab.lib.units import inch

load_dotenv()  # load all the environment variables

# Ensure that the GOOGLE_API_KEY is set
if "GOOGLE_API_KEY" not in os.environ:
    st.error("GOOGLE_API_KEY is not set in the environment variables. Please set it and restart the application.")
    st.stop()

# Initialize genai configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_prompt(language, summary_length):
    word_limits = {
        "brief": 1000,
        "detailed": 1500,
        "comprehensive": 2000
    }
    word_limit = word_limits[summary_length]
    
    base_prompt = f"""Create a {summary_length} summary of the video content in {language}. The summary should be approximately {word_limit} words long.

1. Provide a comprehensive explanation of the main topics discussed in the video.
2. Use bullet points for key information, followed by brief explanations.
3. Include relevant examples or analogies to illustrate concepts.
4. Ensure the summary is in simple, clear {language}.
5. Structure your summary with an introduction, main body, and conclusion.

Summarize the following transcript according to the given instructions:
"""
    return base_prompt

def generate_pdf_report(summary, summary_type, language):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    
    content = []
    
    content.append(Paragraph(f"{summary_type} Summary ({language})", styles['Title']))
    content.append(Spacer(1, 12))
    
    paragraphs = summary.split('\n')
    
    for para in paragraphs:
        if para.strip().startswith('•'):
            content.append(Paragraph(para, styles['Normal']))
        else:
            content.append(Paragraph(para, styles['Justify']))
        content.append(Spacer(1, 6))
    
    doc.build(content)
    buffer.seek(0)
    return buffer.getvalue()

def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        raise e

def generate_summary(transcript_text, language, length):
    model = genai.GenerativeModel("gemini-pro")
    prompt = get_prompt(language, length)
    
    try:
        response = model.generate_content(prompt + transcript_text)
        
        if response.text:
            # Format the summary
            formatted_summary = format_summary(response.text)
            return formatted_summary
        else:
            return "The model couldn't generate a summary due to content restrictions. Please try a different video."
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

def format_summary(summary):
    # Split the summary into paragraphs
    paragraphs = summary.split('\n')
    formatted_summary = ""
    
    for para in paragraphs:
        if para.strip().startswith('•'):
            # This is a bullet point
            formatted_summary += f"{para}\n"
        elif para.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
            # This is a numbered point
            formatted_summary += f"{para}\n"
        else:
            # This is a regular paragraph
            formatted_summary += f"{para}\n\n"
    
    return formatted_summary

# Initialize session state variables
if 'summaries' not in st.session_state:
    st.session_state.summaries = {}
if 'youtube_link' not in st.session_state:
    st.session_state.youtube_link = ""
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "English"
if 'compare_summaries' not in st.session_state:
    st.session_state.compare_summaries = False
if 'selected_length' not in st.session_state:
    st.session_state.selected_length = "Brief"

st.title("YouTube Transcript to Detailed Notes Converter")

youtube_link = st.text_input("Enter YouTube Video Link:", value=st.session_state.youtube_link)
if youtube_link != st.session_state.youtube_link:
    st.session_state.youtube_link = youtube_link
    st.session_state.summaries = {}  # Clear previous summaries when link changes

# Language selection
languages = ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Japanese", "Korean", "Chinese", "Hindi", "Marathi"]
selected_language = st.selectbox("Select summary language:", languages, index=languages.index(st.session_state.selected_language))
if selected_language != st.session_state.selected_language:
    st.session_state.selected_language = selected_language
    st.session_state.summaries = {}  # Clear previous summaries when language changes

# Summary comparison option
compare_summaries = st.checkbox("Generate summaries of different lengths for comparison", value=st.session_state.compare_summaries)
if compare_summaries != st.session_state.compare_summaries:
    st.session_state.compare_summaries = compare_summaries
    st.session_state.summaries = {}  # Clear previous summaries when comparison option changes

# Summary length selection (only shown if compare_summaries is False)
if not compare_summaries:
    summary_lengths = ["Brief", "Detailed", "Comprehensive"]
    selected_length = st.selectbox("Select summary length:", summary_lengths, index=summary_lengths.index(st.session_state.selected_length))
    if selected_length != st.session_state.selected_length:
        st.session_state.selected_length = selected_length
        st.session_state.summaries = {}  # Clear previous summaries when length changes

if youtube_link:
    try:
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    except IndexError:
        st.error("Invalid YouTube URL. Please make sure you've entered a valid YouTube video link.")

if st.button("Get Detailed Notes"):
    try:
        transcript_text = extract_transcript_details(youtube_link)

        if transcript_text:
            if compare_summaries:
                summary_types = ["Brief", "Detailed", "Comprehensive"]
                
                for summary_type in summary_types:
                    if summary_type not in st.session_state.summaries:
                        with st.spinner(f"Generating {summary_type} Summary..."):
                            summary = generate_summary(transcript_text, selected_language, summary_type.lower())
                            st.session_state.summaries[summary_type] = summary
                
                st.success("Summaries generated successfully! You can now view and download the summaries.")
            else:
                if selected_length not in st.session_state.summaries:
                    with st.spinner(f"Generating {selected_length} Summary..."):
                        summary = generate_summary(transcript_text, selected_language, selected_length.lower())
                        st.session_state.summaries[selected_length] = summary
                
                st.success("Summary generated successfully! You can now view and download the summary.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please make sure you've entered a valid YouTube video link and try again.")

# Display summaries and download buttons
if st.session_state.summaries:
    if st.session_state.compare_summaries:
        for summary_type, summary in st.session_state.summaries.items():
            st.markdown(f"## {summary_type} Summary")
            st.markdown(summary)
            
            pdf_report = generate_pdf_report(summary, summary_type, st.session_state.selected_language)
            st.download_button(
                label=f"Download {summary_type} Summary PDF",
                data=pdf_report,
                file_name=f"video_summary_{st.session_state.selected_language}_{summary_type.lower()}.pdf",
                mime="application/pdf",
                key=f"pdf_{summary_type}"
            )
            
            st.markdown("---")
    else:
        summary = st.session_state.summaries[st.session_state.selected_length]
        st.markdown(f"## {st.session_state.selected_length} Summary ({st.session_state.selected_language}):")
        st.markdown(summary)
        
        pdf_report = generate_pdf_report(summary, st.session_state.selected_length, st.session_state.selected_language)
        st.download_button(
            label="Download PDF Summary",
            data=pdf_report,
            file_name=f"video_summary_{st.session_state.selected_language}_{st.session_state.selected_length.lower()}.pdf",
            mime="application/pdf",
            key="pdf_single"
        )
