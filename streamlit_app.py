# Updated and Reordered Streamlit App
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

            if st.session_state.step == 0:
                st.session_state.summary_text = generate_category_summary(df)
                st.session_state.step = 1
                st.rerun()

            if st.session_state.step == 1:
                st.subheader("1️⃣ Category Summary")
                st.write(st.session_state.summary_text)

                st.session_state.bullet_summary = generate_bullet_summary(df)
                st.subheader("2️⃣ Bullet Point Summary")
                st.write(st.session_state.bullet_summary)

                email_body = urllib.parse.quote(st.session_state.bullet_summary)
                mailto_link = f"mailto:?subject=GMP Assessment Summary&body={email_body}"
                st.markdown(f'<a href="{mailto_link}"><button style="margin-top:10px;">📧 Email Summary</button></a>', unsafe_allow_html=True)

                if st.button("Continue to Maturity Gaps"):
                    st.session_state.step = 2
                    st.rerun()

            if st.session_state.step == 2:
                st.subheader("3️⃣ Top 10 Maturity Gaps")
                st.session_state.maturity_gap_df = identify_top_maturity_gaps(df)
                st.dataframe(st.session_state.maturity_gap_df, use_container_width=True)
                if st.button("Continue to Maturity Drivers"):
                    st.session_state.step = 3
                    st.rerun()

            if st.session_state.step == 3:
                st.subheader("4️⃣ Top 10 Maturity Drivers")
                st.session_state.maturity_driver_df = identify_top_maturity_drivers(df)
                st.dataframe(st.session_state.maturity_driver_df, use_container_width=True)
                if st.button("Continue to Recommendations"):
                    st.session_state.step = 4
                    st.rerun()

            if st.session_state.step == 4:
                st.subheader("5️⃣ Capability Recommendations")
                results = run_recommendation_analysis(df)
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
