import os.path
from abc import ABC, abstractmethod
from datetime import datetime

import numpy as np
from PIL import Image

from vidis_algorithms_api.core import settings


class Task(ABC):
    
    @classmethod
    @property
    @abstractmethod
    def name(cls):
        raise NotImplementedError
   
    def _save_task_result(self, layer_data: np.ndarray, hypespecter_path: str):
        basedir = os.path.join(settings.DATA_PATH, hypespecter_path,
                                    settings.CUSTOM_LAYER_FOLDER)
        os.makedirs(basedir, exist_ok=True)
        
        now = datetime.now()
        path_to_save_npy = os.path.join(basedir, f'{self.name}_{now}.npy')
        path_to_save_webp = os.path.join(basedir, f'{self.name}_{now}.webp')
        
        np.save(path_to_save_npy, layer_data)
        image = Image.fromarray(layer_data)
        image.thumbnail((500, 500), Image.ANTIALIAS)
        image.save(path_to_save_webp, "WEBP")
        
        return os.path.join(hypespecter_path, settings.CUSTOM_LAYER_FOLDER, f'{self.name}_{now}.npy')
        

    def run(self, lname, hsi_id, hyperspecter_path, hyperspecter_layout, **kwargs):
        data = np.load(os.path.join(settings.DATA_PATH, hyperspecter_path, "hsi.npy"), mmap_mode="r")
        data = np.transpose(data, hyperspecter_layout)
        result = self.task(hyperspecter=data, **kwargs)
        assert result.ndim == 2, "Result should have two dimensions (height x width)"
        return self._save_task_result(result, hyperspecter_path)
    
    @abstractmethod
    def task(self, hyperspecter: np.ndarray, **kwargs) -> np.ndarray:
        pass
