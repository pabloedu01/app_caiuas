import requests

# URL pré-assinada gerada pela sua API
presigned_url = "https://intranet-caiuas2.s3.amazonaws.com/2026/01/12/9968fbf9-7b25-47fd-b3ca-4e6701b1960e_teste.txt?AWSAccessKeyId=AKIA5QLL2OJAKP4BGEGV&Signature=jmGngyWUaYpL%2FBRn00%2F92s%2B7D34%3D&Expires=1768238381"

with open('teste.txt', 'rb') as f:
    response = requests.put(presigned_url, data=f)
    print("Status:", response.status_code)
    print("Upload concluído!" if response.status_code == 200 else "Erro no upload")