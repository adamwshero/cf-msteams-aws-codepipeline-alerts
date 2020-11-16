import logging
import json
import os
import requests
import boto3

log_level = os.getenv('LOG_LEVEL', 'WARNING')
logger = logging.getLogger()
logger.setLevel(log_level)

msteams_webhook_allAlerts = os.environ['MSTEAMSWEBHOOK_ALLALERTS']
msteams_webhook_onlyFailures = os.environ['MSTEAMSWEBHOOK_ONLYFAILURES']
logger.debug(msteams_webhook_allAlerts)
logger.debug(msteams_webhook_onlyFailures)
codepipeline_client = boto3.client('codepipeline')

def lambda_handler(event, context):
    detail = event['detail']
    codepipeline_name = detail.get('pipeline', 'UNKNOWN_NAME')
    codepipeline_stage = detail.get('stage', 'UNKNOWN_STAGE')
    codepipeline_action = detail.get('action', 'UNKNOWN_ACTION')
    codepipeline_state = detail.get('state', 'UNKNOWN_STATE')
    codepipeline_action_type = detail['type']['provider']

    if codepipeline_state == 'STARTED':
        # Ignore started actions
        return

    pipeline_execution = codepipeline_client.get_pipeline_execution(
        pipelineName=codepipeline_name,
        pipelineExecutionId=detail['execution-id']
    )

    commit_id = pipeline_execution['pipelineExecution']['artifactRevisions'][0]['revisionId'][:8]
    commit_message = pipeline_execution['pipelineExecution']['artifactRevisions'][0]['revisionSummary']
    commit_details = f'{commit_id}: {commit_message}'
    message = f'Code Pipeline State Changed: {codepipeline_name}-{codepipeline_stage}-{codepipeline_action}-{codepipeline_state}'
    data = {
        '@type': 'MessageCard',
        '@context': 'http://schema.org/extensions',
        'summary': message,
        'title': f'{codepipeline_name} CodePipeline Change',
        'text': f'The *{codepipeline_stage}:{codepipeline_action}* action in *{codepipeline_name}* has **{codepipeline_state}**',
        'sections': [{
            # 'activityTitle': 'Code Pipline State Change',
            # 'activitySubtitle': codepipeline_name,
            'facts': [
                {
                    'name': 'Stage',
                    'value': codepipeline_stage,
                },
                {
                    'name': 'Action',
                    'value': codepipeline_action
                },
                {
                    'name': 'Type',
                    'value': codepipeline_action_type
                },
                {
                    'name': 'State',
                    'value': codepipeline_state
                },
                {
                    'name': 'Commit',
                    'value': commit_details
                }
            ]
        }],
        'potentialAction':[
            {
                '@type': 'OpenUri',
                'name': 'View in CodePipeline',
                'targets': [
                    {
                        'os': 'default',
                        'uri': f'https://console.aws.amazon.com/codesuite/codepipeline/pipelines/{codepipeline_name}/view'
                    }
                ]
            }
        ]
    }

    logger.debug(json.dumps(data))
    print(msteams_webhook_allAlerts)
    if msteams_webhook_allAlerts:
        send_to_msteams(data, msteams_webhook_allAlerts)

    if codepipeline_state == 'FAILED' and msteams_webhook_onlyFailures:
        send_to_msteams(data, msteams_webhook_onlyFailures)

def send_to_msteams(data, msteams_webhook):
    requests.post(msteams_webhook, data = json.dumps(data))
