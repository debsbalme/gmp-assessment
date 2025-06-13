# Streamlit App with Sequential Step Buttons (using st.rerun())
import streamlit as st
import pandas as pd
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

                display_breadcrumb(st.session_state.step)

            # Step 0: Category Summary
            if st.session_state.step == 0:
                if st.button("1️⃣ Generate Category Summary"):
                    st.session_state.summary_text = generate_category_summary(df)
                    st.session_state.step = 1
                    st.rerun()

            if st.session_state.step >= 1:
                st.subheader("1️⃣ Category Summary")
                st.write(st.session_state.summary_text)

            # Step 1: Bullet Summary
            if st.session_state.step == 1:
                if st.button("2️⃣ Generate Bullet Summary"):
                    st.session_state.bullet_summary = generate_bullet_summary(df)
                    st.session_state.step = 2
                    st.rerun()

            if st.session_state.step >= 2:
                st.subheader("2️⃣ Bullet Point Summary")
                st.write("Please copy and paste the text below into your email or document.")
                st.code(st.session_state.bullet_summary, language="markdown")

            # Step 2: Maturity Gaps
            if st.session_state.step == 2:
                if st.button("3️⃣ Identify Maturity Drivers"):
                    st.session_state.maturity_gap_df = identify_top_maturity_drivers(df)
                    st.session_state.step = 3
                    st.rerun()

            if st.session_state.step >= 3:
                st.subheader("3️⃣ Maturity Drivers")
                st.dataframe(st.session_state.maturity_gap_df, use_container_width=True)

            # Step 3: Maturity Drivers
            if st.session_state.step == 3:
                if st.button("4️⃣ Identify Maturity Gaps"):
                    st.session_state.maturity_driver_df = identify_top_maturity_gaps(df)
                    st.session_state.step = 4
                    st.rerun()

            if st.session_state.step >= 4:
                st.subheader("4️⃣ Maturity Drivers")
                st.dataframe(st.session_state.maturity_driver_df, use_container_width=True)

            # Step 4: Recommendations
            if st.session_state.step == 4:
                if st.button("5️⃣ Run Recommendations Analysis"):
                    st.session_state.recommendation_results = run_recommendation_analysis(df)
                    st.session_state.step = 5
                    st.rerun()

            if st.session_state.step >= 5:
                st.subheader("5️⃣ Capability Recommendations")
                results = st.session_state.recommendation_results
                if results and results['matched_recommendations']:
                    # Create DataFrame from matched recommendations, which now include the new fields
                    recommendations_df = pd.DataFrame(results['matched_recommendations'])
                    # Rename 'recommendation' column for better display in Streamlit
                    recommendations_df.rename(columns={'recommendation': 'Recommendation'}, inplace=True)
                    recommendations_df.rename(columns={'overview': 'Overview'}, inplace=True)
                    recommendations_df.rename(columns={'gmpimpact': 'GMP Utilization Impact​'}, inplace=True)
                    recommendations_df.rename(columns={'busimpact': 'Business Impact​'}, inplace=True)

                    # Reorder columns for better presentation (optional, but good practice)
                    # Ensure all expected columns are present before reordering
                    expected_cols = [
                        'Recommendation',
                        'overview',
                        'gmpimpact',
                        'businessimpact',
                        'score',
                        'maxweight'
                    ]
                    # Filter for columns that actually exist in the DataFrame
                    display_cols = [col for col in expected_cols if col in recommendations_df.columns]
                    st.dataframe(recommendations_df[display_cols], hide_index=True, use_container_width=True)
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
