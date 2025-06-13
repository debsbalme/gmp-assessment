#app.py
import streamlit as st
import pandas as pd
import time
from datetime import datetime
import urllib
# Import the new function
from recommendation_agent import (
    run_recommendation_analysis,
    generate_category_summary,
    generate_bullet_summary,
    identify_top_maturity_gaps,
    identify_top_maturity_drivers # Import the new function
)

def main():

# Get the current date and time
    now = datetime.now()

# Format the date and time
    formatted_date_time = now.strftime("%Y-%m-%d")

# Display it in Streamlit

    st.image('acx_logo.png',  width=100)
    st.title("GMP Assessment Analysis")
    st.write(f"The current date and time is: **{formatted_date_time}**")
    st.write("Upload a CSV file of the results from the GMP Assessment." \
        " Step through the process to receive the summary, gaps and drivers and recommendations, " \
        " Status of each step is shown in the top corner of the screen by a running man" \
        " At anypoint to restart or provide a different file press the 'Start Over' Button" \
        " This is designed to streamline and standardize the Analysis of the GMP Assessment and not as a complete analysis, each section should be thoroughly read and massaged for client specific language and requirements, please do not just copy and paste straight into deck" \
        " As always this is covered by IPG privacy policy." \
        " Any issues or questions please reach out to deborah.balme@kinesso.com"   )

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            required_columns = ['Category','Question', 'Answer', 'Score', 'MaxWeight']
            if not all(col in df.columns for col in required_columns):
                st.error(f"The uploaded CSV must contain the following columns: **{', '.join(required_columns)}**")
                return

                    st.success("CSV file successfully loaded!, see sample below")
                    st.dataframe(df.head())

                    # Init step state
                    if "step" not in st.session_state:
                        st.session_state.step = 0

                    # Step 0: Generate Category Summary
                    if st.session_state.step == 0:
                        st.session_state.summary_text = generate_category_summary(df)
                        st.session_state.step = 1
                        st.rerun()

        # Step 1: Generate Bullet Summary and Email
        if st.session_state.step == 1:
            st.subheader("1️⃣ Category Summary")
            st.write(st.session_state.summary_text)

            st.subheader("2️⃣ Bullet Point Summary for Sharing")
            st.session_state.bullet_summary = generate_bullet_summary(df)
            st.write(st.session_state.bullet_summary)

            email_body = urllib.parse.quote(st.session_state.bullet_summary)
            mailto_link = f"mailto:?subject=GMP Assessment Summary&body={email_body}"
            st.markdown(f'<a href="{mailto_link}"><button style="margin-top:10px;">📧 Email Summary</button></a>', unsafe_allow_html=True)

            if st.button("Continue to Maturity Gaps"):
                st.session_state.step = 2
                st.rerun()

        # Step 2: Maturity Gaps
        if st.session_state.step == 2:
            st.subheader("3️⃣ Priority Maturity Gaps")
            st.session_state.maturity_gap_df = identify_top_maturity_gaps(df)
            st.dataframe(st.session_state.maturity_gap_df, use_container_width=True)
            if st.button("Continue to Maturity Drivers"):
                st.session_state.step = 3
                st.rerun()

        # Step 3: Maturity Drivers
        if st.session_state.step == 3:
            st.subheader("4️⃣ Priority Maturity Drivers")
            st.session_state.maturity_driver_df = identify_top_maturity_drivers(df)
            st.dataframe(st.session_state.maturity_driver_df, use_container_width=True)
            if st.button("Continue to Recommendations"):
                st.session_state.step = 4
                st.rerun()

        # Step 4: Capability Recommendations
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


# Optional Reset Button
st.markdown("---")
if "step" in st.session_state and st.session_state.step > 0:
    if st.button("🔄 Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


if __name__ == "__main__":
    main()