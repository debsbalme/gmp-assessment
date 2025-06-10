import pandas as pd
import json
import math # For math.isnan to check for NaN values
import streamlit as st

# Define the Recommendation Set as provided in your agent's internal knowledge base
RECOMMENDATION_SET = [
    {
        "question": "which automated bidding strategies have you used in dv360? please give further context of the performance in the comments section.",
        "answer": "n/a",
        "recommendation": "Explore Automated Bidding Strategies in DV360"
    },
    {
        "question": "have you developed or used any of the following custom bidding algorithms in dv360? please give further context of the objectives and performance in the comments section.",
        "answer": "n/a",
        "recommendation": "Explore Custom Bidding Strategies in DV360"
    },
    {
        "question": "which automated bidding strategies have you used in sa360?",
        "answer": "n/a",
        "recommendation": "Explore Automated Bidding Strategies in SA360"
    },
    {
        "question": "have you used any of the cm360's apis? if so, please provide additional detail in the comments box.",
        "answer": "n/a",
        "recommendation": "Utilize CM360 APIs"
    },
    {
        "question": "have you used sa360's api for campaign management and reporting automation? if so, please provide additional detail in the comments box.",
        "answer": ["no - we are currently not using sa360 apis","n/a"],
        "recommendation": "Utilize SA360 APIs"
    },
    {
        "question": "have you used dv360's api for campaign management and reporting automation? if so, please provide additional detail in the comments box.",
        "answer": "n/a",
        "recommendation": "Utilize DV360 APIs"
    },
    {
        "question": "how are you activating first party data within dv360?",
        "answer": "n/a",
        "recommendation": "Utilize 1PD in DV360"
    },
    {
        "question": "how are you activating first party data within sa360?",
        "answer": "n/a",
        "recommendation": "Utilize 1PD in SA360"
    },
    {
        "question": "how are you activating first party data within cm360?",
        "answer": "n/a",
        "recommendation": "Utilize 1PD in CM360"
    },
    {
        "question": "is your instance of google tag manager server-side or client-side?",
        "answer": "gtm (client-side)",
        "recommendation": "Server-Side Tagging (sGTM)"
    },
    {
        "question": "are your platforms set-up to test privacy sandbox apis (such as protected audience api, topics api, attribution reporting api etc)",
        "answer": [
            "yes but we have not begun testing any google privacy sandbox apis",
            "no we have not tested any google privacy sandbox apis, but we would like to understand what is applicable to our business"
        ],
        "recommendation": "Privacy Sandbox API Consultation"
    },
    {
        "set_id": "1pdm",
        "questions": [
            {
                "question": "is bigquery in use for warehousing ga4/ga360 data?",
                "answer": "yes"
            },
            {
                "question": "which of the following describes the way you use data in bigquery?",
                "answer": [
                    "bigquery data is used for warehousing and analyzing ga4 data only",
                    "we have bigquery set up but don't use it"
                ]
            }
        ],
        "recommendation": "GA4 Enhanced Utilization (1P Data Management)"
    },
    {
        "set_id": "adh",
        "questions": [
            {
                "question": "which google products are currently being utilized?",
                "answer": "ads data hub (adh)"
            },
            {
                "question": "to what extent is ads data hub (adh) currently being used by your team(s) for measurement and analysis?",
                "answer": [
                    "we haven't used adh yet but are interested",
                    "we've used it a few times for exploratory or one-off analysis",
                    "we actively use adh for campaign measurement or insights"
                ]
            },
            {
                "question": "in addition to what is currently being utilized what custom adh analysis would you like to undertake ? select all that apply",
                "answer": [
                    "reach & frequency",
                    "audience overlap",
                    "conversion lift",
                    "path to conversion",
                    "other"
                ]
            }
        ],
        "recommendation": "Ads Data Hub Stewardship"
    },
    {
        "set_id": "ga4imp",
        "questions": [
            {
                "question": "which of the following google products are linked to your google analytics instance (ga4/ga360)?",
                "answer": "n/a"
            },
            {
                "question": "which google products are currently being utilized?",
                "answer": [
                    "google analytics 4 (ga4)",
                    "google analytics 360 (ga360)"
                ]
            },
            {
                "question": "do you have ga4/ga360 maintenance in place: tagging, refreshing internal filters, updating channel groupings, reevaluating audiences and segments, etc?",
                "answer": [
                    "platform maintenance processes are implemented but not regularly followed",
                    "no platform maintenance takes place"
                ]
            },
            {
                "question": "which of the following best describes the way you use data in ga4/ga360?",
                "answer": [
                    "we collect only high-level website data and periodically review the basic metics (i.e. page views, unique visitors, bounce rate, top viewed pages) to monitor performance.",
                    "we have it set up but it is currently not being utilized."
                ]
            },
            {
                "question": "are you activating media against audiences built in ga4?",
                "answer": [
                    "no audiences are built in ga4.",
                    "we have built audiences in ga4 but have not used them in media activation."
                ]
            }
        ],
        "recommendation": "GA4 Implementation and Platform Maintenance Audit"
    },
    {
        "set_id": "enhancedconv",
        "questions": [
            {
                "question": "what industry is the brand considered to be in?",
                "answer": [
                    "chemical",
                    "education",
                    "government",
                    "healthcare",
                    "legal",
                    "military",
                    "pharmaceuticals",
                    "toys",
                    "other",
                    "n/a"
                ],
                "type": "negative_choice"
            },
            {
                "question": "have you implemented conversion api's (capi)? if so please specify across which partners capis have been implemented.",
                "answer": [
                    "google enhanced conversions",
                    "google enhanced conversions for leads"
                 ],
                "type": "negative_choice"
            },
            {
                "question": "what google owned & operated inventory is currently being bought in media campaigns?",
                "answer": [
                    "google search",
                    "youtube"
                ]
            },
            {
                "question": "do any of your media campaign conversion points involve the customer sharing pii?",
                "answer": [
                    "yes - at point of conversion we collect advance crm: name, address, email, tel, post code, customerid, maid and more",
                    "yes - at point of conversion we collect basic crm: email and/or maid only"
                ]
            },
            {
                "question": "what are your media campaign goals?",
                "answer": [
                    "acquisition",
                    "direct response",
                    "lead generation",
                    "retention",
                    "sales"
                ]
            }
        ],
        "recommendation": "Enhanced Conversions"
    },
    {
        "set_id": "GCPCDP",
        "questions": [
            {
                "question": "which of the following best describes the types of platforms your organize uses to manage first-party data? select all that apply",
                "answer": [
                    "customer data platform (cdp)"
                ],
                "type": "negative_choice"
            },
            {
                "question": "which google products are currently being utilized?",
                "answer": [
                    "google ads",
                    "display & video 360 (dv360)",
                    "search ads 360 (sa360)"
                ]
            },
            {
                "question": "which google products are currently being utilized?",
                "answer": [
                    "google analytics 4 (ga4)",
                    "google analytics 360 (ga360)"
                ]
            },
            {
                "question": "which google products are currently being utilized?",
                "answer": [
                    "bigquery"
                ]
            },
            {
                "question": "is bigquery in use for warehousing ga4/ga360 data?",
                "answer": [
                    "yes"
                ]
            },
            {
                "question": "approximately what % of the next 12 months media budget is to be allocated to gmp platforms? give answer in percentages 0-100%",
                "answer": [
                    "50-75%",
                    "75-100%"
                ]
            }
        ],
        "recommendation": "GCP as CDP"
    },
    {
        "set_id": "GCPClean",
        "questions": [
            {
                "question": "which of the following data usage activities does your organization currently engage or see value in? select all that apply",
                "answer": [
                    "not currently collaborating or sharing data",
                    "n/a"
                ],
                "type": "negative_choice"
            },
            {
                "question": "how important is data privacy and control when sharing data with external platforms, vendors and partners?",
                "answer": [
                    "very important, data must stay governed and secure at all times",
                    "mostly important, we prefer privacy controls but allow some flexibility",
                    "somewhat important, depends on the partner or use case"
                ]
            }
        ],
        "recommendation": "GCP Data Cleanroom Implementation"
    }
]

# Helper function to normalize answers consistent with agent's rules
# This function will be used for both CSV answers and Recommendation Set answers
def normalize_answer_for_comparison(answer_value):
    # Handle NaN from pandas (e.g., empty cells in CSV)
    if pd.isna(answer_value):
        return ""

    # Convert to string, strip whitespace, convert to lowercase
    normalized_val = str(answer_value).lower().strip()

    # Apply agent's specific handling: if 'n/a' or empty, treat as empty string
    if normalized_val == 'n/a' or normalized_val == '':
        return ""

    return normalized_val

def run_recommendation_agent(df):
    """
    Executes the AI Agent's logic to process DataFrame data, match recommendations,
    and calculate total scores and max weights.
    Takes a pandas DataFrame as input.
    """
    # 1. Data Ingestion and Preparation:
    csv_data_map = {}
    st.subheader("Preprocessed CSV Data (with Score and MaxWeight)")
    for index, row in df.iterrows():
        # Preprocess question key consistently
        question_key = str(row['Question']).lower().strip()
        # Normalize answer using the defined helper function
        answer_value = normalize_answer_for_comparison(row['Answer'])

        # Handle NaN for Score and MaxWeight, default to 0.0 if NaN
        score = row['Score'] if pd.notna(row['Score']) else 0.0
        max_weight = row['MaxWeight'] if pd.notna(row['MaxWeight']) else 0.0

        # Apply agent's specific handling for negative scores/maxweights (set to 0.0)
        score = max(0.0, float(score))
        max_weight = max(0.0, float(max_weight))

        csv_data_map[question_key] = {
            'answer': answer_value,
            'score': score,
            'maxweight': max_weight
        }
        # Optionally display preprocessed data in Streamlit for debugging/transparency
        # st.write(f"Question: {question_key}\nAnswer: '{answer_value}'\nScore: {score}\nMaxWeight: {max_weight}\n---")
    st.write("CSV data preprocessed successfully.")

    # 2. Recommendation Matching and Scoring Algorithm:
    matched_recommendations_with_scores = [] # Store recommendation, score, and maxweight
    total_matched_recommendations = 0
    total_score = 0.0
    total_max_score = 0.0

    for item in RECOMMENDATION_SET:
        if "set_id" not in item:
            # A. Single Question Recommendation
            rec_question = item['question'].lower().strip()
            rec_answer_raw = item['answer']
            rec_recommendation = item['recommendation']
            rec_type = item.get('type')

            csv_entry = csv_data_map.get(rec_question)
            user_answer_from_csv = csv_entry['answer'] if csv_entry else None

            current_condition_met = False
            question_score_to_add = 0.0
            question_max_weight_to_add = 0.0

            # Handle Missing Questions: If rec_question is not in the CSV, this condition is automatically False.
            if user_answer_from_csv is not None:
                # Prepare expected answers from recommendation set, normalizing each
                normalized_rec_answers = []
                if isinstance(rec_answer_raw, list):
                    normalized_rec_answers = [normalize_answer_for_comparison(val) for val in rec_answer_raw]
                else:
                    normalized_rec_answers = [normalize_answer_for_comparison(rec_answer_raw)]

                is_match_found = False
                for expected_normalized_answer in normalized_rec_answers:
                    # Strict comparison after consistent normalization
                    if user_answer_from_csv == expected_normalized_answer:
                        is_match_found = True
                        break

                # Apply type Logic:
                if rec_type == "negative_choice":
                    current_condition_met = not is_match_found
                else:  # default positive match
                    current_condition_met = is_match_found

                if current_condition_met:
                    question_score_to_add = csv_entry.get('score', 0.0)
                    question_max_weight_to_add = csv_entry.get('maxweight', 0.0)

            if current_condition_met:
                matched_recommendations_with_scores.append({
                    'recommendation': rec_recommendation,
                    'score': question_score_to_add,
                    'maxweight': question_max_weight_to_add
                })
                total_matched_recommendations += 1
                total_score += question_score_to_add
                total_max_score += question_max_weight_to_add

        else:
            # B. Grouped Questions Recommendation
            all_sub_questions_match = True
            group_questions = item['questions']
            group_recommendation = item['recommendation']

            # Accumulate scores and max_weights for questions within this *potential* matched group
            current_group_contributing_scores = 0.0
            current_group_contributing_max_weights = 0.0

            for sub_q_item in group_questions:
                sub_q_question = sub_q_item['question'].lower().strip()
                sub_q_answer_raw = sub_q_item['answer']
                sub_q_type = sub_q_item.get('type')

                csv_sub_q_entry = csv_data_map.get(sub_q_question)
                user_answer_from_csv_sub_q = csv_sub_q_entry['answer'] if csv_sub_q_entry else None

                current_sub_q_condition_met = False

                # Handle Missing Questions: If sub_q_question is not in the CSV, this condition is automatically False.
                if user_answer_from_csv_sub_q is not None:
                    # Prepare expected answers for sub-question, normalizing each
                    normalized_sub_q_answers = []
                    if isinstance(sub_q_answer_raw, list):
                        normalized_sub_q_answers = [normalize_answer_for_comparison(val) for val in sub_q_answer_raw]
                    else:
                        normalized_sub_q_answers = [normalize_answer_for_comparison(sub_q_answer_raw)]

                    is_sub_q_match_found = False
                    for expected_normalized_sub_q_ans in normalized_sub_q_answers:
                        # Strict comparison after consistent normalization
                        if user_answer_from_csv_sub_q == expected_normalized_sub_q_ans:
                            is_sub_q_match_found = True
                            break

                    # Apply type Logic:
                    if sub_q_type == "negative_choice":
                        current_sub_q_condition_met = not is_sub_q_match_found
                    else: # default positive match
                        current_sub_q_condition_met = is_sub_q_match_found
                else:
                    # If question not found in CSV or user_answer_from_csv_sub_q is None, it fails the group condition
                    current_sub_q_condition_met = False


                if not current_sub_q_condition_met:
                    all_sub_questions_match = False
                    break  # Break from inner loop as one sub-question failed
                else:
                    # If sub-question matches, add its score/maxweight to the temporary group sums
                    if csv_sub_q_entry: # Ensure csv_sub_q_entry exists to get score/maxweight
                        current_group_contributing_scores += csv_sub_q_entry.get('score', 0.0)
                        current_group_contributing_max_weights += csv_sub_q_entry.get('maxweight', 0.0)

            if all_sub_questions_match:
                matched_recommendations_with_scores.append({
                    'recommendation': group_recommendation,
                    'score': current_group_contributing_scores,
                    'maxweight': current_group_contributing_max_weights
                })
                total_matched_recommendations += 1
                total_score += current_group_contributing_scores
                total_max_score += current_group_contributing_max_weights


    # 3. Output Generation for Streamlit:
    st.subheader("Agent's Output")
    if matched_recommendations_with_scores:
        st.write("Matched Recommendations:")
        for rec_info in matched_recommendations_with_scores:
            st.write(f"- {rec_info['recommendation']} (Score: {rec_info['score']:.2f}, MaxWeight: {rec_info['maxweight']:.2f})")
    else:
        st.write("No recommendations matched based on the provided data.")

    st.markdown("---")
    st.write(f"**Total Number of Recommendations Matched = {total_matched_recommendations}**")
    st.write(f"**Total Matched Score = {total_score:.2f}**")
    st.write(f"**Total Matched MaxWeight = {total_max_score:.2f}**")
    st.markdown("---")

# --- Streamlit UI Code ---
st.title("GMP Audit Recommendation Agent")
st.write("Upload a CSV file containing your audit questions, answers, scores, and max weights to get tailored recommendations.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Read the uploaded CSV file into a pandas DataFrame
        df = pd.read_csv(uploaded_file)

        # Validate required columns
        required_columns = ['Question', 'Answer', 'Score', 'MaxWeight']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Error: The uploaded CSV must contain the following columns: {', '.join(required_columns)}")
        else:
            st.success("CSV file successfully loaded!")
            st.dataframe(df.head()) # Display first few rows of the DataFrame

            if st.button("Run Recommendation Analysis"):
                st.subheader("Running Analysis...")
                run_recommendation_agent(df)

    except Exception as e:
        st.error(f"An error occurred while processing the CSV file: {e}")