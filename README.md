# Orchestrating Credit Check on AWS StepFunction, CallBack Pattern, SQS, and TaskToken.

We will implement a real case, which consists of performing a credit check as part of an approval workflow. As we will see below, the workflow is sort; we have an external " Wallet " system. Which is responsible for telling us if the customer has enough balance or not; with that information, we will know in the step function what should be the next step to follow, If we approve or deny the credit. 
It would not be possible if we did not use taskToken to pause the step machine until the external "wallet." system has finished your work and brought us a result.

See more here: https://gabrieltorreswm.medium.com/building-an-ocr-solution-for-document-analysis-with-aws-textract-and-aws-stepfunctions-81b4932c9443

## Installation

Use the package manager npm to install the dependency and then run serverless to deploy in your AWS account.

```bash
npm install 
serverless deploy 
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
