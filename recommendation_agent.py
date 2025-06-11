import pandas as pd
import json
import math # For math.isnan to check for NaN values
import openai
import streamlit as st
import ast
import re

# Define the Recommendation Set as provided in your agent's internal knowledge base
RECOMMENDATION_SET = [
    {
        "question": "which automated bidding strategies have you used in dv360? please give further context of the performance in the comments section.",
        "answer": "n/a",
        "recommendation": "Explore Automaated Bidding Strategies in DV360"
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

def normalize_answer_for_comparison(answer_value):
    """
    Helper function to normalize answers consistent with agent's rules.
    Used for both CSV answers and Recommendation Set answers.
    """
    if pd.isna(answer_value):
        return ""

    normalized_val = str(answer_value).lower().strip()

    if normalized_val == 'n/a' or normalized_val == '':
        return ""

    return normalized_val

def run_recommendation_analysis(df):
    """
    Executes the AI Agent's logic to process DataFrame data, match recommendations,
    and calculate total scores and max weights.
    Returns a dictionary containing matched recommendations and summary totals.
    """
    csv_data_map = {}
    for index, row in df.iterrows():
        question_key = str(row['Question']).lower().strip()
        answer_value = normalize_answer_for_comparison(row['Answer'])

        score = row['Score'] if pd.notna(row['Score']) else 0.0
        max_weight = row['MaxWeight'] if pd.notna(row['MaxWeight']) else 0.0

        score = max(0.0, float(score))
        max_weight = max(0.0, float(max_weight))

        csv_data_map[question_key] = {
            'answer': answer_value,
            'score': score,
            'maxweight': max_weight
        }

    matched_recommendations_with_scores = []
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

            if user_answer_from_csv is not None:
                normalized_rec_answers = []
                if isinstance(rec_answer_raw, list):
                    normalized_rec_answers = [normalize_answer_for_comparison(val) for val in rec_answer_raw]
                else:
                    normalized_rec_answers = [normalize_answer_for_comparison(rec_answer_raw)]

                is_match_found = False
                for expected_normalized_answer in normalized_rec_answers:
                    if user_answer_from_csv == expected_normalized_answer:
                        is_match_found = True
                        break

                if rec_type == "negative_choice":
                    current_condition_met = not is_match_found
                else:
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

            current_group_contributing_scores = 0.0
            current_group_contributing_max_weights = 0.0

            for sub_q_item in group_questions:
                sub_q_question = sub_q_item['question'].lower().strip()
                sub_q_answer_raw = sub_q_item['answer']
                sub_q_type = sub_q_item.get('type')

                csv_sub_q_entry = csv_data_map.get(sub_q_question)
                user_answer_from_csv_sub_q = csv_sub_q_entry['answer'] if csv_sub_q_entry else None

                current_sub_q_condition_met = False

                if user_answer_from_csv_sub_q is not None:
                    normalized_sub_q_answers = []
                    if isinstance(sub_q_answer_raw, list):
                        normalized_sub_q_answers = [normalize_answer_for_comparison(val) for val in sub_q_answer_raw]
                    else:
                        normalized_sub_q_answers = [normalize_answer_for_comparison(sub_q_answer_raw)]

                    is_sub_q_match_found = False
                    for expected_normalized_sub_q_ans in normalized_sub_q_answers:
                        if user_answer_from_csv_sub_q == expected_normalized_sub_q_ans:
                            is_sub_q_match_found = True
                            break

                    if sub_q_type == "negative_choice":
                        current_sub_q_condition_met = not is_sub_q_match_found
                    else:
                        current_sub_q_condition_met = is_sub_q_match_found
                else:
                    current_sub_q_condition_met = False


                if not current_sub_q_condition_met:
                    all_sub_questions_match = False
                    break
                else:
                    if csv_sub_q_entry:
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

    return {
        'matched_recommendations': matched_recommendations_with_scores,
        'total_matched_recommendations': total_matched_recommendations,
        'total_score': total_score,
        'total_max_score': total_max_score
    }


# (Keep your RECOMMENDATION_SET and normalize_answer_for_comparison function here)

# Place run_recommendation_analysis() function here

# === Step 1: Calculate Maturity Levels ===
#def calculate_maturity_levels(df):
#    category_maturity = df.groupby("Category").agg(
#        total_score=pd.NamedAgg(column="Score", aggfunc="sum"),
#        total_max_weight=pd.NamedAgg(column="MaxWeight", aggfunc="sum")
   # )
#    category_maturity["maturity_level"] = (category_maturity["total_score"] / category_maturity["total_max_weight"] * 100).round(2)
#    return category_maturity.reset_index()


# === Step 2: Generate Category Summaries with GPT ===
def generate_category_summary(df):
    
    subset = df[df["Category"] != "Business"]
    questions = subset["Question"].tolist()
    answers = subset["Answer"].tolist()
    comments = subset["Comment"].fillna("").tolist() if "Comment" in df.columns else []

    prompt = f"""
    You are a strategic Adtech/Martech advisor assessing an advertiser’s maturity based on their audit responses
    Provide a summary using the answers and comments for all questions focusing on their current usage of Google Marketing Platform and their utilization and maturity of the implementation of Adtech and Martech.

    Questions: {questions}
    Answers: {answers}
    Comments: {comments}
    """

    client = openai.OpenAI(api_key=st.secrets["OPEN_AI_KEY"])
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Imagine you are a marketing agency focused on Adtech and Martech and Google Marketing Platform."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7
    )

    summary = response.choices[0].message.content
    return summary


def identify_top_maturity_gaps(df):
    subset = df.copy()

    questions = subset["Question"].tolist()
    answers = subset["Answer"].tolist()
    comments = subset["Comment"].fillna("").tolist() if "Comment" in df.columns else []

    prompt = f"""
You are a strategic Adtech/Martech advisor assessing an advertiser’s maturity based on their audit responses. 
Review the following questions, answers, and comments to identify the **top 10 most critical marketing maturity gaps**.

A "maturity gap" is a disconnect between the current state and a more advanced, effective stage of marketing capability.

Each maturity gap should include:
- A concise **Heading** (e.g., "Lack of First-Party Data Activation")
- A brief **Context** (what the maturity driver is and why it matters)
- A clear **Impact** (how this gap is affecting the advertiser's performance or strategic outcomes)

Return a list of the top 10 gaps as structured objects like:
1. **Heading**: ...
   **Context**: ...
   **Impact**: ...

Questions: {questions}
Answers: {answers}
Comments: {comments}
"""

    client = openai.OpenAI(api_key=st.secrets["OPEN_AI_KEY"])
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a marketing maturity consultant focused on identifying key capability gaps from audits."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0.7
    )

    maturity_gaps_text = response.choices[0].message.content

    # Parse the maturity gaps text into a list of dictionaries
    gaps = []
    gap_entries = re.split(r'\d+\.\s*\*\*Heading\*\*\:', maturity_gaps_text)

    for entry in gap_entries[1:]:
        heading_match = re.search(r'(.*?)\s*\*\*\s*Context\*\*\:', entry, re.DOTALL)
        context_match = re.search(r'\*\*\s*Context\*\*\:\s*(.*?)\s*\*\*\s*Impact\*\*\:', entry, re.DOTALL)
        impact_match = re.search(r'\*\*\s*Impact\*\*\:\s*(.*)', entry, re.DOTALL)

        heading = heading_match.group(1).strip() if heading_match else "N/A"
        context = context_match.group(1).strip() if context_match else "N/A"
        impact = impact_match.group(1).strip() if impact_match else "N/A"

        gaps.append({
            "Heading": heading,
            "Context": context,
            "Impact": impact
        })

    # Create a pandas DataFrame
    mat_gaps_df = pd.DataFrame(gaps)

    return mat_gaps_df
