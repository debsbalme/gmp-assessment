import streamlit as st
import pandas as pd
from recommendation_agent import run_recommendation_analysis # Import the analysis function

st.title("Audit Recommendation Agent")
st.write("Upload a CSV file containing your audit questions, answers, scores, and max weights to get tailored recommendations.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Read the uploaded CSV file into a pandas DataFrame
        df = pd.read_csv(uploaded_file)

        # Validate required columns
        required_columns = ['Question', 'Answer', 'Score', 'MaxWeight']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Error: The uploaded CSV must contain the following columns: **{', '.join(required_columns)}**")
        else:
            st.success("CSV file successfully loaded!")
            st.dataframe(df.head()) # Display first few rows of the DataFrame for verification

            if st.button("Run Recommendation Analysis"):
                st.subheader("Running Analysis...")
                # Call the core logic function from recommendation_agent.py
                results = run_recommendation_analysis(df)

                st.subheader("Agent's Output")
                if results['matched_recommendations']:
                    st.write("Matched Recommendations:")
                    for rec_info in results['matched_recommendations']:
                        st.write(f"- **{rec_info['recommendation']}** (Score: {rec_info['score']:.2f}, MaxWeight: {rec_info['maxweight']:.2f})")
                else:
                    st.write("No recommendations matched based on the provided data.")

                st.markdown("---")
                st.write(f"**Total Number of Recommendations Matched = {results['total_matched_recommendations']}**")
                st.write(f"**Total Matched Score = {results['total_score']:.2f}**")
                st.write(f"**Total Matched MaxWeight = {results['total_max_score']:.2f}**")
                st.markdown("---")

    except Exception as e:
        st.error(f"An error occurred while processing the CSV file. Please check its format and content: {e}")
