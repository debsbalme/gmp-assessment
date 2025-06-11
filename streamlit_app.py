import streamlit as st
import pandas as pd
from recommendation_agent import (
    run_recommendation_analysis,
    generate_category_summary,
    identify_top_maturity_gaps
)

def main():
    st.title("GMP Recommendation Results Agent")
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

            if st.button("Run Recommendation Analysis"):
                st.subheader("1️⃣ Matched Recommendations")
                results = run_recommendation_analysis(df)

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

                st.markdown("---")
                st.write(f"**Total Matched Recommendations:** {results['total_matched_recommendations']}")
                st.write(f"**Total Matched Score:** {results['total_score']:.2f}")
                st.write(f"**Total Matched Max Weight:** {results['total_max_score']:.2f}")
                st.markdown("---")

                # Step 2: Show next button
                if st.button("Generate Category Summary (excl. Business)"):
                    summary = generate_category_summary(df)
                    st.subheader("2️⃣ Category Summary")
                    st.write(summary)

                    # Step 3: Show final button
                    if st.button("Identify Top 10 Maturity Gaps"):
                        maturity_gap_df = identify_top_maturity_gaps(df)
                        st.subheader("3️⃣ Top 10 Maturity Gaps")
                        st.dataframe(maturity_gap_df, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred while processing the CSV file: {e}")

if __name__ == "__main__":
    main()
