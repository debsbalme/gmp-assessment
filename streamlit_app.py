# === app.py ===
import streamlit as st
import pandas as pd
from recommendation_agent import (
    run_recommendation_analysis,
#    calculate_maturity_levels,
    generate_category_summary,
 #   generate_overall_recommendations,
    display_results)


def main():
    st.title("Audit Recommendation Agent")
    st.write("Upload a CSV file containing your audit questions, answers, scores, and max weights to get tailored recommendations.")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            # Read the uploaded CSV file into a pandas DataFrame
            df = pd.read_csv(uploaded_file)

            # Validate required columns
            required_columns = ['Category','Question', 'Answer', 'Score', 'MaxWeight']
            if not all(col in df.columns for col in required_columns):
                st.error(f"Error: The uploaded CSV must contain the following columns: **{', '.join(required_columns)}**")
            else:
                st.success("CSV file successfully loaded!")
                st.dataframe(df.head()) # Display first few rows of the DataFrame for verification

                if st.button("Run Recommendation Analysis"):
                    st.subheader("Running Analysis...")
                    # Call the core logic function from analyzer.py
                    results = run_recommendation_analysis(df)
                    st.write("DEBUG: results['matched_recommendations']")
                    st.write(results['matched_recommendations'])
                #     Calculate category maturity
                  #  maturity_levels = calculate_maturity_levels(df)

                  #  Generate summaries for each category
                    category_summaries = {
                        #cat: generate_category_summary(df, cat)
                        #for cat in df["Category"].unique()
                   #     generate_category_summary(df)
                    }

                    # Generate overall recommendations
                   # overall_recs = generate_overall_recommendations(category_summaries, maturity_levels)

                    # Display results
                  #  display_results(maturity_levels)
                                    #, category_summaries, overall_recs, results)

                    #st.subheader("Agent's Output")
                    if results['matched_recommendations']:
                        st.write("### Matched Recommendations")
                        # Validate all entries are dictionaries
                        if all(isinstance(item, dict) for item in results['matched_recommendations']):
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
                            st.error("Error: Some recommendations are not properly formatted as dictionaries.")
                    else:
                        st.write("No recommendations matched based on the provided data.")

                    st.markdown("---")
                    st.write(f"**Total Number of Recommendations Matched:** {results['total_matched_recommendations']}")
                    st.write(f"**Total Matched Score:** {results['total_score']:.2f}")
                    st.write(f"**Total Matched Max Weight:** {results['total_max_score']:.2f}")
                    st.markdown("---")

        except Exception as e:
            st.error(f"An error occurred while processing the CSV file. Please check its format and content: {e}")

if __name__ == "__main__":
    main()