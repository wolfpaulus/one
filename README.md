## One Lambda to rule them all

LambdaOne GUI
https://le95wslzi8.execute-api.us-west-2.amazonaws.com/Prod/ui/index.html

LambdaOne Api	
POST https://le95wslzi8.execute-api.us-west-2.amazonaws.com/Prod/synthesize
Content-Type: application/json

{
  "scope" : "awscd",
  "text" : "Hello Tom",
  "translate": "False",
  "format" : "mp3"
}


In summary, here is what the Lambda function will do:

- Serve the ./ui/index.hml page (including its resources) when an HTTP GET request for /ui/index.html is received
- Process HTTP POST requests, received at /synthesize
- Call  the translate Lambda function EN2DE to translate the text, if the translation into German is requested
- Call the AWS Polly to synthesize text into speech (mp3)
- Store the submitted text in a DynamoDB
- Log events in a cloud watch log group “/aws/lambda/EN2DE” and keep them for 7 days
- Convert the MP3 into WAV using the native FFmpeg executable (built for amd64 Linux kernels 3.2.0)
- Return the base64 encoded binary data to the requesting HTML page for consumption

A detailed documentation about this projeect can be found here:
[https://wolfpaulus.com/one-lambda-to-rule-them-all/](https://wolfpaulus.com/one-lambda-to-rule-them-all/)

<img src="https://wolfpaulus.com/wp-content/uploads/2020/12/allone-1536x870.jpg">