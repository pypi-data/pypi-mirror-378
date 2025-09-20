import os
from castleguard_sdk.castleguard_base import CastleGuardBase
import requests


class Helper(CastleGuardBase):
    
    def split_text(self, text: str):
        """
        Splits the given text into smaller chunks using the API.

        :param text: Input text string to be split.
        :return: A list of split text chunks if successful, None otherwise.
        """

        url = f'{self.base_url}/helpers/split-text'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        
        params = { "inputText": text }
        
        json_value = None
        
        try:
            response = requests.post(url, headers=headers, params=params)
            if response.status_code != 200:
                self.log(f"Failed to split text: {response.text}", logLevel=3)
                return None
            
            json_value = response.json()
            if json_value is not None:
                return json_value
        except requests.RequestException as e:
            self.log(f"split_text request failed: {e}", logLevel=3)
            return None
        
        return json_value
    
    
    def rag_pdf(self, file_path: str):
        """
        Processes a PDF file with the RAG service.

        :param file_path: Path to the PDF file.
        :return: JSON response from the API containing extracted or processed data,
                 or None if the request fails.
        """

        url = f'{self.base_url}/helpers/rag_pdf'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        
        if file_path.startswith("."):
            file_path = os.path.join(self._get_caller_file_path(), file_path)
        
        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path, f, "application/pdf")}
                response = requests.post(url, headers=headers, files=files)
            
            if response.status_code != 200:
                self.log(f"Failed to process rag_pdf: {response.text}", logLevel=3)
                return None
            
            return response.json()
        except requests.RequestException as e:
            self.log(f"rag_pdf request failed: {e}", logLevel=3)
            return None
        
        
    def pdf_to_text(self, file_path: str):
        """
        Converts a PDF file into a Word (.docx) document using the API.

        :param file_path: Path to the PDF file.
        :return: A dictionary with:
                 - "filename": The suggested output filename from the API, if available.
                 - "content": The raw bytes of the converted DOCX file.
                 Returns None if the request fails.
        """

        url = f'{self.base_url}/helpers/pdf-to-text'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        if file_path.startswith("."):
            file_path = os.path.join(self._get_caller_file_path(), file_path)

        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "application/pdf")}
                response = requests.post(url, headers=headers, files=files, stream=True)

            if response.status_code != 200:
                self.log(f"Failed to convert pdf_to_text: {response.text}", logLevel=3)
                return None

            cd_header = response.headers.get("Content-Disposition")
            filename = None
            if cd_header and "filename=" in cd_header:
                filename = cd_header.split("filename=")[1].strip('"')

            return {
                "filename": filename,
                "content": response.content
            }
        except requests.RequestException as e:
            self.log(f"pdf_to_text request failed: {e}", logLevel=3)
            return None
