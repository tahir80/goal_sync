
import argparse
import uuid


# [START dialogflow_es_detect_intent_text]
def detect_intent_texts(project_id, session_id, text, language_code):
    """Returns the result of detect intent with texts as inputs.
    Using the same `session_id` between requests allows continuation
    of the conversation."""
    # from google.cloud import dialogflow
    # import dialogflow_v2 as dialogflow
    from google.cloud import dialogflow

    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    print("Session path: {}\n".format(session))

   
    text_input = dialogflow.TextInput(text=text, language_code=language_code)

    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
     )

    print("=" * 20)
    print("Query text: {}".format(response.query_result.query_text))
    print(
            "Detected intent: {} (confidence: {})\n".format(
                response.query_result.intent.display_name,
                response.query_result.intent_detection_confidence,
            )
        )
    print("Fulfillment text: {}\n".format(response.query_result.fulfillment_text))


# [END dialogflow_es_detect_intent_text]


if __name__ == "__main__":

    detect_intent_texts(
        "reactpageagent-jypw", "23482734678213478", "ice breaker", "en-US"
    )
