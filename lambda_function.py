import os
import json
from openai import OpenAI

def lambda_handler(event, context):
    try:
        client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        
        body = json.loads(event.get('body', '{}'))
        user_text = body.get('text', '')
        
        if not user_text:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Text is required'})
            }
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_text}
            ]
        )
        
        ai_response = response.choices[0].message.content
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': ai_response
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }