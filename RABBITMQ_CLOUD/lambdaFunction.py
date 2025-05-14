def lambda_handler(event, context):
    message = event.get("text", "")
    CENSOR_LIST = event.get("censor_list", [])

    words = message.split()
    censored = ['****' if word.lower() in [w.lower() for w in CENSOR_LIST] else word for word in words]
    result = ' '.join(censored)

    return {
        'statusCode': 200,
        'body': result
    }
