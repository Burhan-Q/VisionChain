from autodistill_grounding_dino import GroundingDINO
from autodistill_yolov8 import YOLOv8


# define an ontology to map class names to our GroundingDINO prompt
# the ontology dictionary has the format {caption: class}
# where caption is the prompt sent to the base model, and class is the label that will
# be saved for that caption in the generated annotations
# then, load the model
base_model = GroundedSAM(ontology=CaptionOntology({"shipping container": "container"}))

# label all images in a folder called `context_images`
base_model.label("./context_images", extension=".jpeg")
