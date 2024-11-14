import streamlit as st
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
import tempfile
import io

# Initialize recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()

# Define language codes
languages = {
    'Afrikaans': 'af', 'Albanian': 'sq', 'Amharic': 'am', 'Arabic': 'ar', 'Armenian': 'hy',
    'Azerbaijani': 'az', 'Basque': 'eu', 'Belarusian': 'be', 'Bengali': 'bn', 'Bosnian': 'bs',
    'Bulgarian': 'bg', 'Catalan': 'ca', 'Cebuano': 'ceb', 'Chinese (Simplified)': 'zh-CN',
    'Chinese (Traditional)': 'zh-TW', 'Corsican': 'co', 'Croatian': 'hr', 'Czech': 'cs',
    'Danish': 'da', 'Dutch': 'nl', 'English': 'en', 'Esperanto': 'eo', 'Estonian': 'et',
    'Finnish': 'fi', 'French': 'fr', 'Frisian': 'fy', 'Galician': 'gl', 'Georgian': 'ka',
    'German': 'de', 'Greek': 'el', 'Gujarati': 'gu', 'Haitian Creole': 'ht', 'Hausa': 'ha',
    'Hawaiian': 'haw', 'Hebrew': 'he', 'Hindi': 'hi', 'Hmong': 'hmn', 'Hungarian': 'hu',
    'Icelandic': 'is', 'Igbo': 'ig', 'Indonesian': 'id', 'Irish': 'ga', 'Italian': 'it',
    'Japanese': 'ja', 'Javanese': 'jw', 'Kannada': 'kn', 'Kazakh': 'kk', 'Khmer': 'km',
    'Kinyarwanda': 'rw', 'Korean': 'ko', 'Kurdish': 'ku', 'Kyrgyz': 'ky', 'Lao': 'lo',
    'Latin': 'la', 'Latvian': 'lv', 'Lithuanian': 'lt', 'Luxembourgish': 'lb', 'Macedonian': 'mk',
    'Malagasy': 'mg', 'Malay': 'ms', 'Malayalam': 'ml', 'Maltese': 'mt', 'Maori': 'mi',
    'Marathi': 'mr', 'Mongolian': 'mn', 'Myanmar (Burmese)': 'my', 'Nepali': 'ne',
    'Norwegian': 'no', 'Nyanja (Chichewa)': 'ny', 'Odia (Oriya)': 'or', 'Pashto': 'ps',
    'Persian': 'fa', 'Polish': 'pl', 'Portuguese': 'pt', 'Punjabi': 'pa', 'Romanian': 'ro',
    'Russian': 'ru', 'Samoan': 'sm', 'Scots Gaelic': 'gd', 'Serbian': 'sr', 'Sesotho': 'st',
    'Shona': 'sn', 'Sindhi': 'sd', 'Sinhala (Sinhalese)': 'si', 'Slovak': 'sk', 'Slovenian': 'sl',
    'Somali': 'so', 'Spanish': 'es', 'Sundanese': 'su', 'Swahili': 'sw', 'Swedish': 'sv',
    'Tagalog (Filipino)': 'tl', 'Tajik': 'tg', 'Tamil': 'ta', 'Tatar': 'tt', 'Telugu': 'te',
    'Thai': 'th', 'Turkish': 'tr', 'Turkmen': 'tk', 'Ukrainian': 'uk', 'Urdu': 'ur',
    'Uyghur': 'ug', 'Uzbek': 'uz', 'Vietnamese': 'vi', 'Welsh': 'cy', 'Xhosa': 'xh',
    'Yiddish': 'yi', 'Yoruba': 'yo', 'Zulu': 'zu'
}

"""
Initialize session state variables to manage application states:
- `languages_selected`: To store selected language pairs.
- `conversation_started`: To track the start or end of a conversation.
"""
if 'languages_selected' not in st.session_state:
    st.session_state.languages_selected = {}

if 'conversation_started' not in st.session_state:
    st.session_state.conversation_started = False


def language_selection():
    """
    Step 1: Language selection interface
    - Allow users to select input and desired languages for both patient and healthcare provider.
    - Save selected languages in session state for later use.
    """
    st.title("Healthcare Translation App")
    st.subheader("Select Languages")

    # Dropdown menus for language selection
    patient_lang = st.selectbox("Select speaking language for Patient", options=list(languages.keys()))
    patient_desired_lang = st.selectbox("Select output desired language for Patient", options=list(languages.keys()))
    healthcare_lang = st.selectbox("Select speaking language for Healthcare Provider", options=list(languages.keys()))
    healthcare_desired_lang = st.selectbox("Select output desired language for Healthcare Provider",
                                           options=list(languages.keys()))

    # Proceed button to save selections
    proceed = st.button("Proceed")

    if proceed:
        # Save selected language codes in session state
        st.session_state.languages_selected = {
            'patient_lang_code': languages[patient_lang],
            'patient_desired_lang_code': languages[patient_desired_lang],
            'healthcare_lang_code': languages[healthcare_lang],
            'healthcare_desired_lang_code': languages[healthcare_desired_lang]
        }
        st.write("Language selection complete. Proceed to start the conversation.")
        st.session_state.conversation_started = True

        # Display selected languages for confirmation
        st.write(f"Patient Language: {patient_lang} ({languages[patient_lang]})")
        st.write(f"Patient desired Language: {patient_desired_lang} ({languages[patient_desired_lang]})")
        st.write(f"Healthcare Language: {healthcare_lang} ({languages[healthcare_lang]})")
        st.write(f"Healthcare desired Language: {healthcare_desired_lang} ({languages[healthcare_desired_lang]})")


def capture_and_translate(input_lang_code, output_lang_code):
    """
    Step 2: Capture and translate speech input
    - Use speech recognition to capture spoken input.
    - Translate the recognized text to the desired language.
    - Handle errors and provide feedback.
    """
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    try:
        recognized_text = recognizer.recognize_google(audio, language=input_lang_code)
        translated_text = translator.translate(recognized_text, src=input_lang_code, dest=output_lang_code).text
        return recognized_text, translated_text
    except Exception as e:
        st.error(f"Error recognizing or translating: {str(e)}")
        return None, None


def play_audio(text, lang_code):
    """
    Step 3: Text-to-speech conversion and audio playback
    - Generate audio for the translated text using gTTS.
    - Return the temporary audio file for playback.
    """
    tts = gTTS(text=text, lang=lang_code)
    tmp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp_audio_file.name)
    return tmp_audio_file


def show_conversation_interface():
    """
    Step 4: Conversation interface
    - Allow patient and healthcare provider to speak, translate their inputs, and generate responses.
    - Maintain a log of the conversation for review or download.
    """
    # Fetch language codes from session state
    patient_lang_code = st.session_state.languages_selected['patient_lang_code']
    healthcare_lang_code = st.session_state.languages_selected['healthcare_lang_code']
    patient_desired_lang_code = st.session_state.languages_selected['patient_desired_lang_code']
    healthcare_desired_lang_code = st.session_state.languages_selected['healthcare_desired_lang_code']

    # Initialize conversation log if not already done
    if 'conversation_log' not in st.session_state:
        st.session_state.conversation_log = []

    # Start and End conversation controls
    st.markdown("<h3 style='text-align: center;'>Conversation Controls</h3>", unsafe_allow_html=True)

    if st.button("Start Conversation"):
        st.session_state.conversation_started = True
        st.write("Conversation started. Press Speak to communicate.")

    if st.button("End Conversation"):
        st.session_state.conversation_started = False
        st.write("Conversation ended. Download the conversation log below.")

        # Display and download conversation log if available
        if st.session_state.conversation_log:
            conversation_log_text = "\n".join(
                [
                    f"{entry['speaker']}:\nOriginal: {entry['original_text']}\nTranslated: {entry['translated_text']}\n"
                    for entry in st.session_state.conversation_log
                ]
            )
            st.text_area("Conversation Log", value=conversation_log_text, height=300)
            st.download_button(
                label="Download Conversation Log",
                data=conversation_log_text,
                file_name="conversation_log.txt",
                mime="text/plain"
            )
            st.session_state.conversation_log = []

    if st.session_state.conversation_started:
        # Interface for patient and provider communication
        col1, col2 = st.columns(2)

        with col1:
            st.header("Patient")
            if st.button("Speak - Patient"):
                patient_text, patient_translated = capture_and_translate(patient_lang_code,
                                                                         healthcare_desired_lang_code)
                if patient_text:
                    st.write("Patient's Original Text:", patient_text)
                    st.write("Patient's Translated Text:", patient_translated)
                    st.session_state.conversation_log.append(
                        {"speaker": "Patient", "original_text": patient_text, "translated_text": patient_translated})
                    patient_audio = play_audio(patient_translated, healthcare_desired_lang_code)
                    st.audio(patient_audio.name)

        with col2:
            st.header("Healthcare Provider")
            if st.button("Speak - Healthcare Provider"):
                healthcare_text, healthcare_translated = capture_and_translate(healthcare_lang_code,
                                                                               patient_desired_lang_code)
                if healthcare_text:
                    st.write("Provider's Original Text:", healthcare_text)
                    st.write("Provider's Translated Text:", healthcare_translated)
                    st.session_state.conversation_log.append(
                        {"speaker": "Healthcare Provider", "original_text": healthcare_text,
                         "translated_text": healthcare_translated})
                    healthcare_audio = play_audio(healthcare_translated, patient_desired_lang_code)
                    st.audio(healthcare_audio.name)


# Run the application
language_selection()
if st.session_state.conversation_started:
    show_conversation_interface()
