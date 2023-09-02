from autodistill_grounded_sam import GroundedSAM
from super_gradients.training import models
from super_gradients.common.object_names import Models
from autodistill.detection import CaptionOntology
from autodistill_yolov8 import YOLOv8

import super_gradients
import typer
from tqdm import tqdm
import os
from PIL import Image
import fiftyone as fo
from typing import List
from dataclasses import dataclass


@dataclass
class Cropper:
    """
    Should better generalise this.
    """
    model_name: str = 'fastest' 

    def __post_init__(self):
        assert self.model_name in ['yolo_nas_l', 'yolo_nas_m', 'yolo_nas_s'], (
            'Selected model is not available'
        ) 
        self.model = models.get(Models.YOLO_NAS_M, pretrained_weights="coco")

    def predict(self, source: str, file_paths: List[str]) -> List[fo.Detection]:
        
        predictions = self.model.predict(source)

        dataset = fo.Dataset()
        print(f'Postprocessing predictions')
        for prediction, file_path in tqdm(zip(predictions, file_paths)):

            sample = fo.Sample(os.path.abspath(file_path))

            class_names = prediction.class_names
            predictions = prediction.prediction

            im = Image.open(file_path)
            width, height = im.size

            detections = []

            for bbox, score, label in zip(
                predictions.bboxes_xyxy,
                predictions.confidence.astype(float),
                predictions.labels.astype(int),
            ):

                rel_box = [
                    bbox[0] / width,
                    bbox[1] / height,
                    (bbox[2] - bbox[0]) / width,
                    (bbox[3] - bbox[1]) / height,
                ]
     
                detection = fo.Detection(
                    label=class_names[label],
                    bounding_box=rel_box,
                    confidence=score,
                )
                detections.append(detection)

            sample['prediction'] = fo.Detections(detections=detections)
            sample.save()

        return dataset



def main(
    limit: int = None,
):
    """
    GroundedSAM to crop then DINO + QDrant to classify!
    """

    cropper = Cropper(model_name='yolo_nas_s')

    dir_path = "/home/ubuntu/VisionChain/src/demo/bottles_dataset/data"
    file_paths = [
        os.path.join(dir_path, file_name) for file_name in os.listdir(dir_path)
    ]

    if limit is not None:
        file_paths = file_paths[:limit]

    dataset = cropper.predict(dir_path + '/*.jpg', file_paths) 

    session = fo.launch_app(dataset, remote=True, address="0.0.0.0", desktop=True)
    session.wait()


if __name__ == "__main__":
    typer.run(main)
