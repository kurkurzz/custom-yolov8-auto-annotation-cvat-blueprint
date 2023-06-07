
import io
import base64
import json

import cv2
import numpy as np
from ultralytics import YOLO

# Initialize your model
def init_context(context):
	context.logger.info('Init context...  0%')
	model = YOLO('custom-yolov8n.pt')
	context.user_data.model_handler = model
	context.logger.info('Init context...100%')

# Inference endpoint
def handler(context, event):
	context.logger.info('Run custom yolov8 model')
	data = event.body
	image_buffer = io.BytesIO(base64.b64decode(data['image']))
	image = cv2.imdecode(np.frombuffer(image_buffer.getvalue(), np.uint8), cv2.IMREAD_COLOR)

	results = context.user_data.model_handler(image)
	result = results[0]

	boxes = result.boxes.data[:,:4]
	confs = result.boxes.conf
	clss = result.boxes.cls
	class_name = result.names

	detections = []
	threshold = 0.1
	for box, conf, cls in zip(boxes, confs, clss):
		label = class_name[int(cls)]
		if conf >= threshold:
			# must be in this format
			detections.append({
				'confidence': str(float(conf)),
				'label': label,
				'points': box.tolist(),
				'type': 'rectangle',
			})

	return context.Response(body=json.dumps(detections), headers={},
		content_type='application/json', status_code=200)

