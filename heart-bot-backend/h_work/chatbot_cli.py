import requests
import os

base_url = "http://127.0.0.1:8000/"

def combined_prediction_cli():
    while True:
        print("\nChoose an option:")
        print("1. Chat with the LLM (text-based predictions)")
        print("2. Upload an X-ray image and provide symptoms for combined prediction")
        print("3. Exit")
        
        choice = input("Enter your choice (1/2/3): ")
        
        if choice == "1":
            # Chat with the LLM (text-based predictions)
            user_input = input("Enter your symptom or question: ")
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            
            # Send the input to the FastAPI chatbot endpoint
            try:
                response = requests.get(f"{base_url}chatbot/", params={"input_text": user_input})
                response_data = response.json()
                
                # Ensure that the 'response' key exists in the response_data
                if 'response' in response_data:
                    print(f"Bot response: {response_data['response']}")
                else:
                    print(f"Error: No response found in the server's reply.")
                    
            except requests.exceptions.RequestException as e:
                print(f"Error: Unable to connect to the chatbot server. {e}")

        elif choice == "2":
            # Upload an X-ray image and provide symptoms for combined prediction
            image_path = input("Enter the path to the X-ray image: ")
            user_input = input("Enter your symptoms or question: ")
            
            if not os.path.exists(image_path):
                print("Error: The image file does not exist.")
                continue
            
            # Open the image file in binary mode
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                params = {'input_text': user_input}
                
                # Send the image and text to FastAPI server for combined prediction
                try:
                    response = requests.post(f"{base_url}combined-prediction/", files=files, data=params)
                    response_data = response.json()
                    print(f"Combined Prediction Results: {response_data}")
                except requests.exceptions.RequestException as e:
                    print(f"Error: Unable to connect to the server. {e}")

        elif choice == "3":
            # Exit the CLI
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please choose 1, 2, or 3.")

# Run the combined prediction CLI
if __name__ == "__main__":
    combined_prediction_cli()
