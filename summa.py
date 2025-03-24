import streamlit as st
import cohere
import docx

# Replace with your actual Cohere API key
API_KEY = "WIArC8GebX86Vj6SxyRkQVc7VcEfKTe2Dt3BFAV0"

# Initialize Cohere Client
co = cohere.Client(API_KEY)

# Function to extract text from a Word document
def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Streamlit UI
st.title("🩺 Lung Cancer Report Q&A Chatbot")
st.write("Upload a Word document related to lung cancer, get a summary, and ask questions interactively.")

# Session state to store chat history & summary
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "document_summary" not in st.session_state:
    st.session_state.document_summary = ""

# File uploader
uploaded_file = st.file_uploader("📄 Upload a Word Document", type=["docx"])

document_text = ""
if uploaded_file is not None:
    document_text = extract_text_from_docx(uploaded_file)
    st.success("✅ Document uploaded successfully!")

    # Generate AI summary (only once per upload)
    if not st.session_state.document_summary:
        with st.spinner("Summarizing document..."):
            summary_response = co.generate(
                model="command",
                prompt=f"Summarize the following medical report in a concise way:\n\n{document_text}",
                max_tokens=150
            )
            st.session_state.document_summary = summary_response.generations[0].text

# Display document summary
if st.session_state.document_summary:
    st.subheader("📌 Summary of the Report")
    st.write(st.session_state.document_summary)

# Display chat history
st.subheader("💬 Chat History")
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["question"])
    with st.chat_message("assistant"):
        st.write(chat["answer"])
        st.write("_As this helped you understand the report? Please let me know if you would like any other information extracted._")  # This is only displayed, not included in download

# User input for question
user_question = st.text_input("🔎 Ask your question:")

if st.button("Ask"):
    if document_text and user_question:
        with st.spinner("Generating answer..."):
            response = co.generate(
                model="command",
                prompt=f"Based on the following medical report, answer the question concisely:\n\nReport:\n{document_text}\n\nQuestion: {user_question}",
                max_tokens=300
            )
            answer = response.generations[0].text

        # Append to chat history (excluding extra message)
        st.session_state.chat_history.append({"question": user_question, "answer": answer})

        # Refresh the page to show the new chat message
        st.rerun()

# Download chat button (excluding extra message)
if st.session_state.chat_history:
    chat_text = "\n\n".join([f"User: {c['question']}\nAI: {c['answer']}" for c in st.session_state.chat_history])  # No extra message included
    st.download_button("📥 Download Chat", chat_text, "chat_history.txt", "text/plain")
