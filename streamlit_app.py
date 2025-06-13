# Streamlit App with Clipboard Copy Custom Component
import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
from recommendation_agent import (
    run_recommendation_analysis,
    generate_category_summary,
    generate_bullet_summary,
    identify_top_maturity_gaps,
    identify_top_maturity_drivers
)

def main():
    now = datetime.now()
    formatted_date_time = now.strftime("%Y-%m-%d")

    st.image('acx_logo.png', width=100)
    st.title("GMP Assessment Analysis")
    st.write(f"The current date and time is: **{formatted_date_time}**")
    st.write("Upload a CSV file of the results from the GMP Assessment. Step through the process to receive the summary, bullet points, gaps, drivers and recommendations. This tool helps streamline and standardize GMP Assessment analysis.")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            required_columns = ['Category', 'Question', 'Answer', 'Score', 'MaxWeight']
            if not all(col in df.columns for col in required_columns):
                st.error(f"The uploaded CSV must contain the following columns: **{', '.join(required_columns)}**")
                return

            st.success("CSV file successfully loaded! See sample below.")
            st.dataframe(df.head())

            if "step" not in st.session_state:
                st.session_state.step = 0

            # Step 0: Category Summary
            if st.button("1️⃣ Generate Category Summary"):
                st.session_state.summary_text = generate_category_summary(df)
                st.session_state.step = 1

            if st.session_state.step >= 1:
                st.subheader("1️⃣ Category Summary")
                st.write(st.session_state.summary_text)

            # Step 1: Bullet Summary
            if st.button("2️⃣ Generate Bullet Summary"):
                st.session_state.bullet_summary = generate_bullet_summary(df)
                st.session_state.step = 2

            if st.session_state.step >= 2:
                st.subheader("2️⃣ Bullet Point Summary")
                st.write("Please copy and paste this Bullet Summary into an email and share with the team.")
                st.write(st.session_state.bullet_summary)

                # Display the summary and a copy-to-clipboard button using custom JS
                st.code(st.session_state.bullet_summary, language="markdown")
                st.markdown(
                    f"""
                    <button onclick="navigator.clipboard.writeText(`{st.session_state.bullet_summary}`)">📋 Copy to Clipboard</button>
                    """,
                    unsafe_allow_html=True
                )

            # Step 2: Maturity Gaps
            if st.button("3️⃣ Identify Maturity Gaps"):
                st.session_state.maturity_gap_df = identify_top_maturity_gaps(df)
                st.session_state.step = 3

            if st.session_state.step >= 3:
                st.subheader("3️⃣ Top Maturity Gaps")
                st.dataframe(st.session_state.maturity_gap_df, use_container_width=True)

            # Step 3: Maturity Drivers
            if st.button("4️⃣ Identify Maturity Drivers"):
                st.session_state.maturity_driver_df = identify_top_maturity_drivers(df)
                st.session_state.step = 4

            if st.session_state.step >= 4:
                st.subheader("4️⃣ Top Maturity Drivers")
                st.dataframe(st.session_state.maturity_driver_df, use_container_width=True)

            # Step 4: Recommendations
            if st.button("5️⃣ Run Recommendations Analysis"):
                st.session_state.recommendation_results = run_recommendation_analysis(df)
                st.session_state.step = 5

            if st.session_state.step >= 5:
                st.subheader("5️⃣ Capability Recommendations")
                results = st.session_state.recommendation_results
                if results['matched_recommendations']:
                    recommendations_df = pd.DataFrame(results['matched_recommendations'])
                    recommendations_df.rename(columns={'recommendation': 'Recommendation'}, inplace=True)
                    st.dataframe(recommendations_df, hide_index=True, use_container_width=True)
                else:
                    st.info("No recommendations matched based on the provided data.")
                st.write(f"**Total Recommendations:** {results['total_matched_recommendations']}")

        except Exception as e:
            st.error(f"An error occurred while processing the CSV file: {e}")

    if "step" in st.session_state and st.session_state.step > 0:
        if st.button("🔄 Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
