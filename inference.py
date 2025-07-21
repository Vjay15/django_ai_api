import streamlit as st
import requests
import hashlib
import json
import pandas as pd
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="AI Evaluation API Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


BASE_URL = "http://localhost:8000"
# Model configurations
MODELS = {
    "OpenAI GPT-4.1 Mini": {
        "domain": "opai",
        "description": "Fine-tuned GPT-4.1 Mini for expert answer evaluation",
        "host": "opai.localhost"
    },
    "Social Science Llama": {
        "domain": "op.soc", 
        "description": "Quantized Llama-3-8B for social science evaluation",
        "host": "op.soc.localhost"
    },
    "Science Llama": {
        "domain": "op.sci",
        "description": "Quantized Llama-3-8B for science evaluation", 
        "host": "op.sci.localhost"
    }
}

# API Keys for each model
API_KEYS = {
    "opai": "370d931dd462639e4e3209efdf5497c5",
    "op.soc": "23933c8a27b11efe9e76092d34379ac2",
    "op.sci": "8936841114b293000bff13a74cfc7f9b"
}

host_mapping = {
        "opai": "opai.localhost",
        "op.soc": "op.soc.localhost", 
        "op.sci": "op.sci.localhost"
    }
class APIClient:
    def __init__(self, domain, api_key):
        self.domain = domain
        self.api_key = api_key
        self.host = host_mapping[domain]
    
    def get_headers(self, data=None):
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json',
            'Host': self.host
        }
        
        if data is not None:
            json_string = json.dumps(data, separators=(',', ':'))
            content_hash = hashlib.sha256(json_string.encode('utf-8')).hexdigest()
            headers['X-Content-Hash'] = content_hash
            return headers, json_string
            
        return headers, None
    
    def get_model_info(self):
        """Get AI model information"""
        try:
            headers, _ = self.get_headers()
            response = requests.get(f"{BASE_URL}/ai/info", headers=headers)
            if response.status_code == 200:
                return response.json(), None
            else:
                return None, f"Error {response.status_code}: {response.text}"
        except Exception as e:
            return None, str(e)
    
    def generate_response(self, prompt):
        """Generate AI response"""
        try:
            data = {"prompt": prompt}
            headers, json_data = self.get_headers(data)
            
            response = requests.post(
                f"{BASE_URL}/ai/generate/", 
                data=json_data,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json(), None
            else:
                return None, f"Error {response.status_code}: {response.text}"
        except Exception as e:
            return None, str(e)

    def get_history(self):
        """Get user's history"""
        try:
            headers, _ = self.get_headers()
            response = requests.get(f"{BASE_URL}/history/", headers=headers)

            if response.status_code == 200:
                return response.json(), None
            else:
                return None, f"Error {response.status_code}: {response.text}"
        except Exception as e:
            return None, str(e)

def main():
    st.title("🤖 AI Evaluation API Interface")
    st.markdown("### Interact with multiple AI models for academic evaluation")
    
    # Sidebar for model selection
    st.sidebar.title("⚙️ Configuration")
    
    selected_model = st.sidebar.selectbox(
        "Select AI Model:",
        options=list(MODELS.keys()),
        help="Choose which AI model to use for evaluation"
    )
    
    model_config = MODELS[selected_model]
    domain = model_config["domain"]
    api_key = API_KEYS[domain]
    
    # Display model info in sidebar
    st.sidebar.markdown(f"**Model:** {selected_model}")
    st.sidebar.markdown(f"**Description:** {model_config['description']}")
    st.sidebar.markdown(f"**Domain:** {domain}")
    
    # Initialize API client
    client = APIClient(domain, api_key)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["💬 Generate Response", "📊 Model Information", "📜 History"])
    
    with tab1:
        st.header("Generate AI Response")
        
        # Input form
        with st.form("evaluation_form"):
            st.markdown("#### 📝 Input Fields:")
            
            col1, col2 = st.columns(2)
            with col1:
                question = st.text_area(
                    "Question:",
                    height=100,
                    help="Enter the question to be evaluated"
                )
                
                rubrics = st.text_area(
                    "Rubrics:",
                    height=100,
                    help="Enter the evaluation criteria and mark distribution"
                )
            
            with col2:
                answer = st.text_area(
                    "Student Answer:",
                    height=100,
                    help="Enter the student's answer to be evaluated"
                )
                
                total_marks = st.number_input(
                    "Total Marks:",
                    min_value=1,
                    max_value=100,
                    value=5,
                    help="Total marks for this question"
                )
            
            difficulty = st.selectbox(
                "Difficulty Level:",
                ["easy", "medium", "hard"],
                index=1,
                help="Select the difficulty level of the question"
            )
            
            submitted = st.form_submit_button("🚀 Generate Response", type="primary")
            
            if submitted and question and answer and rubrics:
                # Create the prompt from individual fields
                prompt_data = {
                    "question": question,
                    "answer": answer,
                    "rubrics": rubrics,
                    "total_marks": total_marks,
                    "difficulty": difficulty
                }
                
                with st.spinner(f"Generating response using {selected_model}..."):
                    result, error = client.generate_response(json.dumps(prompt_data))
                    print(result,error)
                    if error:
                        st.error(f"❌ Error: {error}")
                    else:
                        st.success("✅ Response generated successfully!")
                        
                        # Display the input data in a structured format
                        st.markdown("#### 📋 Evaluation Input:")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Question:** {question}")
                            st.markdown(f"**Total Marks:** {total_marks}")
                            st.markdown(f"**Difficulty:** {difficulty}")
                        with col2:
                            st.markdown(f"**Student Answer:** {answer}")
                            st.markdown(f"**Rubrics:** {rubrics}")
                        
                        # Display response
                        if isinstance(result, dict) and "response" in result:
                            response_text = result["response"]
                        else:
                            response_text = str(result)
                        
                        st.markdown("#### 🤖 AI Response:")
                        
                        # Try to parse and display structured AI response
                        try:
                            # Try to parse as JSON first
                            response_data = json.loads(response_text)
                            
                            col3, col4 = st.columns(2)
                            with col3:
                                st.markdown("**Score:**")
                                st.text_input("", value=str(response_data.get('Score', 'N/A')), disabled=True, key="current_score")
                                
                                st.markdown("**Explanation:**")
                                st.text_area("", value=response_data.get('Explanation', 'N/A'), height=100, disabled=True, key="current_exp")
                            
                            with col4:
                                st.markdown("**Feedback:**")
                                st.text_area("", value=response_data.get('Feedback', 'N/A'), height=100, disabled=True, key="current_feed")

                        except json.JSONDecodeError:
                            st.error("❌ Error parsing AI response.")

                        # Show raw JSON for debugging
                        with st.expander("🔍 View Raw Response"):
                            st.json(result)
            
            elif submitted:
                st.warning("⚠️ Please fill in all required fields: Question, Answer, and Rubrics.")
    
    with tab2:
        st.header("📊 Model Information")
        
        if st.button("🔄 Refresh Model Info", type="secondary"):
            with st.spinner("Fetching model information..."):
                info, error = client.get_model_info()
                
                if error:
                    st.error(f"❌ Error fetching model info: {error}")
                else:
                    st.success("✅ Model information retrieved!")
                    
                    # Display model info in a nice format
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 🏷️ Basic Information")
                        if isinstance(info, dict):
                            st.markdown(f"**Model Name:** {info.get('model_name', 'N/A')}")
                            st.markdown(f"**Version:** {info.get('version', 'N/A')}")
                            st.markdown(f"**Last Updated:** {info.get('last_updated', 'N/A')}")
                            st.markdown(f"**Accuracy:** {info.get('accuracy', 'N/A')}")
                        
                        st.markdown("#### 💰 Pricing")
                        if isinstance(info, dict) and 'pricing' in info:
                            pricing = info['pricing']
                            st.markdown(f"**Per Request:** {pricing.get('per_request', 'N/A')}")
                            st.markdown(f"**Bulk Discount:** {pricing.get('bulk_discount', 'N/A')}")
                    
                    with col2:
                        st.markdown("#### ⚡ Technical Specs")
                        if isinstance(info, dict) and 'limitations' in info:
                            limits = info['limitations']
                            st.markdown(f"**Max Tokens:** {limits.get('max_tokens', 'N/A')}")
                            st.markdown(f"**Context Window:** {limits.get('context_window', 'N/A')}")
                            st.markdown(f"**Rate Limits:** {limits.get('rate_limits', 'N/A')}")
                        
                        st.markdown("#### 🎯 Capabilities")
                        if isinstance(info, dict) and 'capabilities' in info:
                            for capability in info['capabilities']:
                                st.markdown(f"• {capability}")
                    
                    # Show full JSON
                    with st.expander("🔍 View Full Model Information"):
                        st.json(info)
    
    with tab3:
        st.header("📜 Request History")
        
        if st.button("🔄 Refresh History", type="secondary"):
            st.rerun()
        
        with st.spinner("Fetching history..."):
            history, error = client.get_history()
            if error:
                st.error(f"❌ Error fetching history: {error}")
            else:
                if isinstance(history, list):
                    if history:
                        st.success(f"✅ Found {len(history)} records")

                        # Convert to DataFrame for better display
                        df_data = []
                        for idx, record in enumerate(history, 1):
                            df_data.append({
                                "ID": record.get('id', idx),
                                "Input": record.get('input', '')[:100] + "..." if len(record.get('input', '')) > 100 else record.get('input', ''),
                                "Output": record.get('output', '')[:100] + "..." if len(record.get('output', '')) > 100 else record.get('output', ''),
                            })
                        
                        if df_data:
                            df = pd.DataFrame(df_data)
                            st.dataframe(df, use_container_width=True)
                            
                            # Detailed view
                            st.markdown("#### 🔍 Detailed View")
                            selected_id = st.selectbox("Select record to view details:", [record['ID'] for record in df_data])
                            
                            if selected_id:
                                selected_record = next((r for r in history if r.get('id') == selected_id), None)
                                if selected_record:
                                    # Try to parse the input as JSON to display structured data
                                    input_text = selected_record.get('input', '')
                                    output_text = selected_record.get('output', '')
                                    
                                    try:
                                        input_data = json.loads(input_text)
                                        
                                        # Display structured input
                                        st.markdown("#### 📋 Input Details:")
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            st.markdown("**Question:**")
                                            st.text_area("", value=input_data.get('question', 'N/A'), height=100, disabled=True, key=f"q_{selected_id}")
                                            
                                            st.markdown("**Total Marks:**")
                                            st.text_input("", value=str(input_data.get('score', 'N/A')), disabled=True, key=f"tm_{selected_id}")
                                            
                                            st.markdown("**Difficulty:**")
                                            st.text_input("", value=input_data.get('difficulty', 'N/A'), disabled=True, key=f"d_{selected_id}")
                                        
                                        with col2:
                                            st.markdown("**Student Answer:**")
                                            st.text_area("", value=input_data.get('answer', 'N/A'), height=100, disabled=True, key=f"a_{selected_id}")
                                            
                                            st.markdown("**Rubrics:**")
                                            st.text_area("", value=input_data.get('rubrics', 'N/A'), height=100, disabled=True, key=f"r_{selected_id}")
                                        
                                        st.markdown("#### 🤖 AI Evaluation:")
                                        
                                        # Try to parse the AI output as JSON or extract structured information
                                        try:
                                            # Try to parse as JSON first
                                            output_data = json.loads(output_text)
                                            
                                            col3, col4 = st.columns(2)
                                            with col3:
                                                st.markdown("**Score:**")
                                                st.text_input("", value=str(output_data.get('Score', 'N/A')), disabled=True, key=f"score_{selected_id}")
                                                
                                                st.markdown("**Explanation:**")
                                                st.text_area("", value=output_data.get('Explanation', 'N/A'), height=100, disabled=True, key=f"exp_{selected_id}")

                                            with col4:
                                                st.markdown("**Feedback:**")
                                                st.text_area("", value=output_data.get('Feedback', 'N/A'), height=100, disabled=True, key=f"feed_{selected_id}")

                                        except json.JSONDecodeError:
                                           st.warning("⚠️ Unable to parse AI output as JSON. Displaying raw text instead.")
                                           st.markdown("**Raw AI Output:**")
                                           st.markdown(output_text)
                                    except Exception as e:
                                        st.error(f"⚠️ An error occurred while processing AI output: {e}")
                                
                                else:
                                    st.info("📝 No history records found. Try making some API calls first!")
                            else:
                                st.warning("⚠️ Unexpected response format from history endpoint.")

if __name__ == "__main__":
    main()
