import json
import urllib.request
import urllib.error
import re

# Colab上のFastAPIエンドポイント
API_ENDPOINT = "https://a246-34-139-17-203.ngrok-free.app/predict"

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # 認証されたユーザー情報（必要に応じて使用）
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")

        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])

        print("Processing message:", message)

        # Colab APIに渡すシンプルなリクエストボディ
        request_payload = json.dumps({
            "message": message
        }).encode('utf-8')

        # HTTPリクエストの設定
        req = urllib.request.Request(
            API_ENDPOINT,
            data=request_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        # API呼び出し
        try:
            with urllib.request.urlopen(req) as res:
                response_body = res.read().decode('utf-8')
                response_json = json.loads(response_body)
                assistant_response = response_json.get("response", "")
        except urllib.error.HTTPError as e:
            error_message = e.read().decode('utf-8')
            raise Exception(f"HTTPError from Colab API: {error_message}")

        # 会話履歴に追加
        messages = conversation_history.copy()
        messages.append({"role": "user", "content": message})
        messages.append({"role": "assistant", "content": assistant_response})

        # 成功レスポンス
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }

    except Exception as error:
        print("Error:", str(error))

        # エラーレスポンス
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
