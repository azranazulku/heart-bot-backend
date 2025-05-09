import numpy as np
import torch
import torchxrayvision as xrv
import torchvision


class XRayScanEvaluationRepository:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(XRayScanEvaluationRepository, cls).__new__(cls)
        return cls._instance


    # Prediction function for X-ray classification
    def __get_xray_prediction(self, image: np.array, cuda: bool = False):
        # Load the X-ray model
        xray_model = xrv.models.get_model("densenet121-res224-all")

        image = xrv.datasets.normalize(image, 255)

        if len(image.shape) > 2:
            image = image[:, :, 0]  # Use the first channel if RGB
        if len(image.shape) < 2:
            raise ValueError("Error: Image is not valid.")

        image = image[None, :, :]  # Add batch dimension
        transform = torchvision.transforms.Compose(
            [xrv.datasets.XRayCenterCrop(), xrv.datasets.XRayResizer(224)],
            )
        image = transform(image)

        if cuda:
            image = torch.from_numpy(image).unsqueeze(0).cuda()
            xray_model.cuda()
        else:
            image = torch.from_numpy(image).unsqueeze(0)

        with torch.no_grad():
            preds = xray_model(image).cpu()

        preds_dict = dict(zip(
            xrv.datasets.default_pathologies, 
            preds[0].detach().numpy(),
        ))
        
        # Convert NumPy objects to native Python types for serialization
        preds_dict = {key: float(value) if isinstance(value, np.float32) else value for key, value in preds_dict.items()}
        
        return preds_dict


    def evaluate_xray_scan(
            self, 
            xray_scan: np.array,
        ) -> dict:
        """
        Evaluate X-ray scan and provide diagnosis.
        - **xray_scan**: The X-ray scan file to be evaluated.
        - **Returns**: A JSON response with the evaluation result.
        - **Raises**: 400 if the input is invalid, 500 for internal server errors.
        """
        result = self.__get_xray_prediction(xray_scan)
        if result is None:
            raise ValueError("Error: Image is not valid.")
        return result
