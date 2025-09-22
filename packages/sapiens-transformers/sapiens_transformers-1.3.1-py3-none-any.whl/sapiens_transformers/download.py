"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
class DownloadHF():
	def __init__(self, model_path=''):
		model_path = model_path.strip() if type(model_path) == str else str(model_path).strip()
		if 'https://huggingface.co/' in model_path:
			url = model_path
			if url[-1] == '/': url = url[:-1]
			url = url.split('https://huggingface.co/')[-1]
			if url.count('/') > 1:
				url = url.split('/', 2)
				url.pop()
				url = url[0]+'/'+url[-1]
			model_path = url
		self.__destination_path = None
		def get_default_model(model_path=''):
			result_path = model_path
			model_path = model_path.lower().strip()
			models_list = ('entity-1b-censored', 'entity-10b-vision', 'entity-14b-1m', 'entity-1b-uncensored', 'entity-3b-censored', 'entity-3b-uncensored', 'entity_2-3b-censored',
			'hurlm-1b', 'sapama-10b_hur', 'sapama-3b', 'sapi_audio-0_5b', 'sapi_audiogen-0_5b', 'sapi_image-10b-en', 'sapi_imagegen-2b', 'sapi_moe_8x3b-24b_plus_hur', 'sapi_musicgen-3b',
			'sapi_photogen-12b', 'sapi_video-7b-en', 'sapi_videogen-0_5b', 'sapi_zero-2b', 'sapi_zero-5b', 'sapi-4b', 'sapi-8b-1m', 'sapi-8b-1m_hur', 'sapi-10b-vision', 'sapi-50b_hur',
			'sapi-50b-reasoning_hur', 'sapi-70b_hur', 'sapiens-0_5b', 'sapiens-10b', 'sapiens-10b-reasoning-en', 'sapiens-1b', 'sapiens-2b', 'sapiens-5b', 'sapiens-5b-reasoning-en',
			'sapiens-7b-1m', 'sapiens_2-30b_hur', 'sapiens_code-2b_hur', 'sapiens_code-32b_hur', 'sapiens_imagegen-0_5b', 'sapiens_videogen-2b', 'sapiens_vision-2b', 'sapiens_vision-5b',
			'sapiens-14b-1m', 'sapiens-14b-1m_hur', 'sapiens-30b', 'sapiens-30b_hur', 'sapiens-72b-turbo_hur', 'sapiens-72b_hur', 'sastral-7b-en')
			if model_path.startswith(('./', '/')): model_path = model_path[model_path.find('/')+1:]
			if model_path.endswith('/'): model_path = model_path[:-1]
			if model_path in models_list:
				from sapiens_transformers.adaptations import NAME067
				result_path = NAME067+str(models_list.index(model_path)+1).rjust(3, '0')
				self.__destination_path = model_path
			return result_path
		model_path = get_default_model(model_path=model_path)
		try: from huggingface_hub import snapshot_download
		except: snapshot_download = None
		from os import makedirs
		from requests import Session
		session = Session()
		session.timeout = 3600
		self.__model_path, self.__makedirs, self.__snapshot_download = model_path, makedirs, snapshot_download
		self.__warning = 'Set the model name or address in the "model_path" parameter of the class constructor.'
	def native_snapshot_download(self, destination_path=''):
		try:
			if len(self.__model_path) > 0:
				if self.__destination_path and not destination_path: destination_path = self.__destination_path
				destination_path = destination_path.strip() if isinstance(destination_path, str) else str(destination_path).strip()
				if len(destination_path) < 1: destination_path = self.__model_path.split('/')[-1].strip()
				self.__makedirs(destination_path, exist_ok=True)
				api_url = f'https://huggingface.co/api/models/{self.__model_path}'
				from requests import get
				from os import path
				from tqdm import tqdm
				response = get(api_url)
				if response.status_code != 200: return False
				files = [file['rfilename'] for file in response.json().get('siblings', [])]
				base_url = f'https://huggingface.co/{self.__model_path}/resolve/main/'
				for file in files:
					url = base_url + file
					file_path = path.join(destination_path, file)
					response = get(url, stream=True)
					if response.status_code == 200:
						self.__makedirs(path.dirname(file_path), exist_ok=True)
						total_size = int(response.headers.get('content-length', 0))
						with open(file_path, 'wb') as local_file, tqdm(desc=file, total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as progress_bar:
							for chunk in response.iter_content(chunk_size=8192):
								local_file.write(chunk)
								progress_bar.update(len(chunk))
					else: return False
			else:
				print(self.__warning)
				return False
			return True
		except: return False
	def snapshot_download(self, destination_path=''):
		try:
			if len(self.__model_path) > 0:
				if self.__destination_path and not destination_path: destination_path = self.__destination_path
				destination_path = destination_path.strip() if type(destination_path) == str else str(destination_path).strip()
				if len(destination_path) < 1: destination_path = self.__model_path.split('/')[-1].strip()
				self.__makedirs(destination_path, exist_ok=True)
				if self.__snapshot_download is None: return self.native_snapshot_download(destination_path=destination_path)
				else: self.__snapshot_download(repo_id=self.__model_path, local_dir=destination_path, force_download=True)
				return True
			else:
				print(self.__warning)
				return False
		except: return self.native_snapshot_download(destination_path=destination_path)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
