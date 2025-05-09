from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
import torchxrayvision as xrv
import skimage.io
import torchvision
import numpy as np
import io

# Initialize FastAPI app
app = FastAPI()

# Load pre-trained DistilBERT tokenizer and model
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased')

# Load the X-ray model
xray_model = xrv.models.get_model("densenet121-res224-all")

def get_text_prediction(text: str):
    print(f"Processing text: {text}")
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    logits = outputs.logits
    prediction = torch.argmax(logits, dim=1).item()
    confidence = torch.max(torch.softmax(logits, dim=1)).item()  # Confidence score for the predicted class

    # Based on the prediction, return a more detailed response
    if prediction == 0:
        response = {
            "diagnosis": "No disease detected based on the input text.",
            "suggestions": [
                "Continue monitoring the patient for any new symptoms.",
                "If symptoms persist or worsen, consider scheduling further tests.",
                "Ensure regular checkups and health screenings as per the patient's profile."
            ],
            "confidence": confidence
        }
    elif prediction == 1:
        response = {
            "diagnosis": "Disease detected based on the input text, further diagnosis needed.",
            "suggestions": [
                "Consider conducting more specific tests such as X-ray, MRI, or blood work.",
                "Referral to a specialist (e.g., cardiologist, neurologist) may be necessary.",
                "Monitor the patient closely for any changes in symptoms and severity."
            ],
            "confidence": confidence
        }
    else:  # For multi-class cases, you can handle other predictions
        response = {
            "diagnosis": "Further evaluation needed, the model detected a different condition.",
            "suggestions": [
                "Consider conducting additional tests.",
                "Referral to a specialist might be necessary.",
                "Monitor closely for changes in symptoms."
            ],
            "confidence": confidence
        }

    # Return the detailed response
    return response


# Prediction function for X-ray classification
def get_xray_prediction(image: np.array, cuda: bool = False):
    print(f"Received image with shape: {image.shape}")
    image = xrv.datasets.normalize(image, 255)

    if len(image.shape) > 2:
        image = image[:, :, 0]  # Use the first channel if RGB
    if len(image.shape) < 2:
        return "Error: Image is not valid."

    image = image[None, :, :]  # Add batch dimension
    transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop(), xrv.datasets.XRayResizer(224)])
    image = transform(image)

    if cuda:
        image = torch.from_numpy(image).unsqueeze(0).cuda()
        xray_model.cuda()
    else:
        image = torch.from_numpy(image).unsqueeze(0)

    with torch.no_grad():
        preds = xray_model(image).cpu()

    preds_dict = dict(zip(xrv.datasets.default_pathologies, preds[0].detach().numpy()))
    
    # Convert NumPy objects to native Python types for serialization
    preds_dict = {key: float(value) if isinstance(value, np.float32) else value for key, value in preds_dict.items()}
    
    return preds_dict

# Function to interpret DenseNet predictions using LLM
def interpret_xray_predictions(preds_dict):
    # Convert the prediction dictionary into a textual prompt for the LLM
    xray_info = ""
    for pathology, score in preds_dict.items():
        xray_info += f"{pathology}: {score:.2f}, "
    
    # Trim the last comma and space
    xray_info = xray_info.rstrip(", ")
    
    # Create a prompt for the LLM
    prompt = f"Given the following X-ray results: {xray_info}, please interpret these results in a natural language, explaining any significant findings and what they might mean for the patient."

    # Get the LLM to interpret the X-ray prediction results
    return get_text_prediction(prompt)  # Reusing the get_text_prediction function to process the prompt with LLM

# Combine text and X-ray predictions
def combine_predictions(text: str, image: np.array):
    # Get the text prediction
    text_response = get_text_prediction(text)
    
    # Get the X-ray prediction
    xray_predictions = get_xray_prediction(image)
    
    # Interpret X-ray prediction using the LLM
    xray_interpretation = interpret_xray_predictions(xray_predictions)
    
    # Combine both into a single response
    combined_response = {
        "text_prediction": text_response,
        "xray_prediction": xray_predictions,
        "xray_interpretation": xray_interpretation
    }
    
    return combined_response

@app.post("/combined-prediction/")
async def combined_prediction(file: UploadFile = File(...), input_text: str = ""):
    # Read the file as a byte stream
    image_bytes = await file.read()
    print("Received image data")

    # Convert byte stream to a numpy array
    image = skimage.io.imread(io.BytesIO(image_bytes))
    print(f"Image shape after loading: {image.shape}")
    
    # Check if image is grayscale or color
    if len(image.shape) > 2:
        print("Image has multiple channels, using only the first channel")
    else:
        print("Image is grayscale")

    # Get combined predictions
    result = combine_predictions(input_text, image)
    
    # Return the result in the expected format with a 'response' key
    return JSONResponse(content={"response": result})

@app.get("/chatbot/")  # Endpoint to process text input (symptoms)
async def chatbot(input_text: str):
    # Process the input text through the model for prediction
    response = get_text_prediction(input_text)
    return JSONResponse(content={"response": response})

@app.get("/")
def read_root():
    return {"message": "Welcome to the heart disease prediction API!"}

