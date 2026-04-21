def test_annotation_format():

# first defines a funciton, which will tests the annotaiotn service by a readable string. 
    
    event = {
        "event_id": "evt_1",
        # unique id for tracking each event 

        
        "image_id": "img_1",

        # id taht idenfifies each image 
        "path": "images/test.jpg",

        # locaiton 
        "label": "cat",
        # descprtion of th inferince service 
        "confidence": 0.95

        # 
    }

    annotation = {
        "event_id": event["event_id"],
        "image_id": event["image_id"],
        "path": event["path"],
        "annotation": f"{event['label']} ({event['confidence']:.2f})",
        "status": "annotation_completed"
    }

    assert annotation["annotation"] == "cat (0.95)"
