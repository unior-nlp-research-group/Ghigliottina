import requests
import json
import base64
from key import GOOGLE_VISION_API_KEY
import logging
import re

'''
Google Vision API request documentation
https://cloud.google.com/vision/docs/reference/rest/v1/images/annotate
'''

def detect_clues(image_content=None, image_uri=None):

    assert (image_content or image_uri)

    payload = {
        "requests": [
            {
                'image': {
                #    "content": image_content,
                #    "source": {
                #        "imageUri": image_uri
                #    }
                },
                'features': [
                    {
                        'type': 'TEXT_DETECTION',
                        'maxResults': 10
                    }
                ],
                'imageContext': {
                    'languageHints': ['it']
                }
            }
        ]
    }

    if image_content:
        payload["requests"][0]['image']['content'] = image_content
    else:
        payload["requests"][0]['image']['source'] = { "imageUri": image_uri }

    payload = json.dumps(payload)

    response = requests.request(
        "POST", 
        url = "https://vision.googleapis.com/v1/images:annotate",
        data=payload, 
        headers={'Content-Type': "application/json"}, 
        params = {"key": GOOGLE_VISION_API_KEY}
    )    

    result_json = response.json()
    logging.info('detect_clues response: {}'.format(result_json))
    text_annotations = result_json.get('responses',[{}])[0].get('textAnnotations', None)
    if text_annotations:
        clues = get_clues_from_annotations(text_annotations)
        clues_csv = ', '.join(clues)
        logging.info('VISION: {} detected clues: {}'.format(len(clues), clues_csv))
        return clues
    return []

def get_clues_from_annotations(text_annotations):

    boxes = []

    for annotation in text_annotations:
        description = annotation['description']
        if re.match(r"[\d\.]+", description): # the price
            continue
        #if description in ['Rai','Rai1','Rai1HD','HD']
        #    continue
        vertices = annotation['boundingPoly']['vertices']
        x = vertices[0]['x'] + round((vertices[1]['x'] - vertices[0]['x'])/2)
        y = vertices[0]['y']
        boxes.append({
            'description': description,
            'x': x,
            'y': y
        })
    logging.info('VISION: detected text: {}'.format(', '.join(b['description'] for b in boxes)))

    n = len(boxes)
    if n > 5:
        boxes = sorted(boxes, key=lambda b:(b['y'],b['x']))
        delta_x_matrix = [[0 for i in range(n)] for j in range(n)]
        for i in range(n):
            for j in range(n):                
                delta_x_matrix[i][j] = abs(boxes[i]['x'] - boxes[j]['x'])
        start_delta_sum = [
            {
                'start': s,
                'delta_sum': sum(delta_x_matrix[i][j] for i in range(s,s+5) for j in range(s,s+5))
            }
            for s in range(n-5+1)
        ]
        start_delta_sum = sorted(start_delta_sum, key=lambda x:x['delta_sum'])
        best_start = start_delta_sum[0]['start']
        boxes = boxes[best_start:best_start+5]

    clues = [b['description'].replace('0','O').replace('1','I') for b in boxes]
    return clues



def test_get_clues():
    file_path = 'vision_test.json'
    structure = json.load(open(file_path))
    text_annotations = structure['responses'][0]['textAnnotations']
    return get_clues_from_annotations(text_annotations)

def get_image_content_by_uri(file_uri):
    response = requests.get(file_uri)
    img_content = base64.standard_b64encode(response.content).decode("utf-8") 
    return img_content

def test():
    #img_path = "/Users/fedja/Downloads/ghigliottinabotlogo.png"
    #img_path = "/Users/fedja/Downloads/robot.png"
    img_path = "/Users/fedja/Downloads/ghigliottina_test/one.jpg"
    with open(img_path, "rb") as imageFile:
        img_content = base64.standard_b64encode(imageFile.read()).decode("utf-8") 

    text_list = detect_clues(img_content)
    print(text_list)

def test_url():
    url = 'https://api.telegram.org/file/bot692434140:AAGO2Vx__BS9-PP_qhup-mKasOlfxTQt6qo/photos/file_3.jpg'
    img_content = get_image_content_by_uri(url)
    text_list = detect_clues(img_content)
    print(text_list)
    
#if __name__ == "__main__":
#    print(test_get_clues())