import streamlit as st
import pandas as pd
from recommendation_agent import (
    run_recommendation_analysis,
    generate_category_summary,
    identify_top_maturity_gaps
)

def main():
    st.title("GMP Assessment Analysis")
    st.write("Upload a CSV file to receive tailored audit recommendations and marketing maturity insights.")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            required_columns = ['Category','Question', 'Answer', 'Score', 'MaxWeight']
            if not all(col in df.columns for col in required_columns):
                st.error(f"The uploaded CSV must contain the following columns: **{', '.join(required_columns)}**")
                return

            st.success("CSV file successfully loaded!")
            st.dataframe(df.head())

            # Initialize session state
            if "step" not in st.session_state:
                st.session_state.step = 0

            # Step 1: Run Recommendation Analysis
            if st.session_state.step == 0:
                if st.button("Run Recommendation Analysis"):
                    st.session_state.recommendation_results = run_recommendation_analysis(df)
                    st.session_state.step = 1
                    st.experimental_rerun()

            # Step 2: Show Recommendations
            if st.session_state.step >= 1:
                results = st.session_state.recommendation_results
                st.subheader("1️⃣ Matched Recommendations")
                if results['matched_recommendations']:
                    recommendations_df = pd.DataFrame(results['matched_recommendations'])
                    recommendations_df['score'] = recommendations_df['score'].round(2)
                    recommendations_df['maxweight'] = recommendations_df['maxweight'].round(2)
                    recommendations_df.rename(columns={
                        'recommendation': 'Recommendation',
                        'score': 'Score',
                        'maxweight': 'Max Weight'
                    }, inplace=True)
                    st.dataframe(recommendations_df, hide_index=True, use_container_width=True)
                else:
                    st.info("No recommendations matched based on the provided data.")

                st.write(f"**Total Matched Recommendations:** {results['total_matched_recommendations']}")
                st.write(f"**Total Matched Score:** {results['total_score']:.2f}")
                st.write(f"**Total Matched Max Weight:** {results['total_max_score']:.2f}")
                st.markdown("---")

                if st.session_state.step == 1 and st.button("Generate Category Summary (excl. Business)"):
                    st.session_state.summary_text = generate_category_summary(df)
                    st.session_state.step = 2
                    st.experimental_rerun()

            # Step 3: Show Category Summary
            if st.session_state.step >= 2:
                st.subheader("2️⃣ Category Summary")
                st.write(st.session_state.summary_text)

                if st.session_state.step == 2 and st.button("Identify Top 10 Maturity Gaps"):
                    st.session_state.maturity_gap_df = identify_top_maturity_gaps(df)
                    st.session_state.step = 3
                    st.experimental_rerun()

            # Step 4: Show Maturity Gaps
            if st.session_state.step >= 3:
                st.subheader("3️⃣ Top 10 Maturity Gaps")
                st.dataframe(st.session_state.maturity_gap_df, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred while processing the CSV file: {e}")

# Optional Reset Button
st.markdown("---")
if "step" in st.session_state and st.session_state.step > 0:
    if st.button("🔄 Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


if __name__ == "__main__":
    main()
