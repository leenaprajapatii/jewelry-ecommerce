from django.core.mail import send_mail

def send_custom_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        "leenaprajapati004@gmail.com",  # Replace with your email
        recipient_list,
        fail_silently=False,
    )



# import requests

# API_URL = "https://goldapi.io/api/"
# HEADERS = {
#     "x-access-token": "goldapi-apv72wsm7iwmcq9-io",  # Your API key
#     "Content-Type": "application/json"
# }

# def get_metal_rates():
#     try:
#         gold_response = requests.get(f"{API_URL}XAU/USA", headers=HEADERS)
#         silver_response = requests.get(f"{API_URL}XAG/INR", headers=HEADERS)

#         gold_data = gold_response.json()
#         silver_data = silver_response.json()

#         return {
#             "gold_rate": gold_data.get("price", "N/A"),
#             "silver_rate": silver_data.get("price", "N/A"),
#         }
#     except Exception as e:
#         print("Error fetching metal rates:", e)
#         return {"gold_rate": "N/A", "silver_rate": "N/A"}
