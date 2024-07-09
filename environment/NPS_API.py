def api_docs():
    import json
    api_docs = {
        "base_url": "<https://developer.nps.gov/api/v1/>",
        "endpoints": {
            "/alerts": {
                        "method": "GET",
                        "description": "Retrieve park alerts.",
                        "parameters": None,
                        "response": [
                                        {
                                        "category": "Information",
                                        "description": "Some destinations are unavailable because of construction related to the Canyon Overlooks and Trails Restoration Project.",
                                        "id": "4C3095E2-1DD8-B71B-0BAC8E16AABF3113",
                                        "parkCode": "yell",
                                        "title": "Area Closures in Canyon",
                                        "url": "https://www.nps.gov/yell/planyourvisit/canyonprojects.htm",
                                        "lastIndexedDate": "2023-06-27 14:10:21.0",
                                        "relatedRoadEvents": []
                                        },
                                        {
                                        "category": "Caution",
                                        "description": "The road between Roaring Mountain and Willow Park is under construction. Expect delays up to 30 minutes and night closures June 11–September 10 from 10pm–7am (excluding Saturday nights).",
                                        "id": "696FC8C9-1DD8-B71B-0BF3D47A2BF92890",
                                        "parkCode": "yell",
                                        "title": "Construction & Nightly Closures between Norris & Mammoth Hot Springs",
                                        "url": "https://www.nps.gov/yell/planyourvisit/parkroads.htm",
                                        "lastIndexedDate": "2023-06-27 14:10:21.0",
                                        "relatedRoadEvents": [
                                                                {
                                                                "title": "Crazy Squirrels",
                                                                "id": "68BC589E-7FFC-4AFC-AD02-85E123C4C145",
                                                                "type": "roadevent",
                                                                "url": "https://www.nps.gov/yose/planyourvisit/conditions.htm"
                                                                }
                                                                ]
                                        }
                        ]
                                    
                        }   
                    }
                }

    # Convert the dictionary to a JSON string
    api_docs = json.dumps(api_docs, indent=2)
    return api_docs