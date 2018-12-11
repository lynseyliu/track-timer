import cv2
import numpy as np


class YoloCV:
    version = 'yolov2-tiny'
    args = {
        'config':  'object-detection-opencv/' + version + '.cfg',
        'weights': 'object-detection-opencv/' + version + '.weights',
        #'classes': 'object-detection-opencv/yolov3.txt',
        'classes': 'object-detection-opencv/person.txt',
    }
    scale = 0.00392
    classes = None
    COLORS = None
    net = None

    def __init__(self):
        with open(self.args['classes'], 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
            self.COLORS = np.random.uniform(
                0, 255, size=(len(self.classes), 3))
            self.net = cv2.dnn.readNet(
                self.args['weights'], self.args['config'])

    def get_output_layers(self, net):

        layer_names = net.getLayerNames()

        output_layers = [layer_names[i[0] - 1]
                         for i in net.getUnconnectedOutLayers()]

        return output_layers

    def draw_prediction(self, img, x, y, x_plus_w, y_plus_h, class_id):

        #label = str(self.classes[class_id])

        #color = (self.COLORS[class_id])
        color = (255, 0, 0)

        cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)

        # cv2.putText(img, label, (x-10, y-10),
        #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    def getPrediction(self, image):
        Width = image.shape[1]
        Height = image.shape[0]

        blob = cv2.dnn.blobFromImage(
            image, self.scale, (416, 416), (0, 0, 0), True, crop=False)

        self.net.setInput(blob)

        outs = self.net.forward(self.get_output_layers(self.net))

        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.5
        nms_threshold = 0.4

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])

        indices = cv2.dnn.NMSBoxes(
            boxes, confidences, conf_threshold, nms_threshold)

        boxesResult = []

        for i in indices:
            i = i[0]
            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            box_data = {
                'x': x,
                'y': y,
                'w': w,
                'h': h,
                'class_id': class_ids[i]
            }
            boxesResult.append(box_data)
            # self.draw_prediction(image, class_ids[i], confidences[i], round(
            #    x), round(y), round(x+w), round(y+h))
        return boxesResult

        # cv2.imwrite("object-detection.jpg", image)
        # cv2.destroyAllWindows()
