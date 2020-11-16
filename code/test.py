import json
data = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": 'message',
        "sections": [{
        "activityTitle": "Code Pipeline State Change",
        "activitySubtitle": 'code_pipeline_name',
        "facts": [
            {
            "name": "Stage",
            "value": 'code_pipeline_stage',
            },
            {
            "name": "Action",
            "value": 'code_pipeline_action'
            },
            {
            "name": "State",
            "value": 'code_pipeline_state'
            }
        ]
        }]
}

print(json.dumps(data))