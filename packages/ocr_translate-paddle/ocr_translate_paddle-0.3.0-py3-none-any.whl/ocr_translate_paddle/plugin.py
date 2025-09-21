###################################################################################
# ocr_translate-hugging_face - a plugin for ocr_translate                         #
# Copyright (C) 2023-present Davide Grassano                                      #
#                                                                                 #
# This program is free software: you can redistribute it and/or modify            #
# it under the terms of the GNU General Public License as published by            #
# the Free Software Foundation, either version 3 of the License.                  #
#                                                                                 #
# This program is distributed in the hope that it will be useful,                 #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                  #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                   #
# GNU General Public License for more details.                                    #
#                                                                                 #
# You should have received a copy of the GNU General Public License               #
# along with this program.  If not, see {http://www.gnu.org/licenses/}.           #
#                                                                                 #
# Home: https://github.com/Crivella/ocr_translate-hugging_face                    #
###################################################################################
"""ocr_translate plugin to allow loading of PaddleOCR."""
import importlib
import logging
import os
from pathlib import Path

import numpy as np
from ocr_translate import models as m
from PIL import Image

logger = logging.getLogger('plugin')

LOADED = False
PaddleOCR = None  # pylint: disable=invalid-name

class EnvMixin:
    """Mixin class to handle environment variables."""
    def __init__(self, *args, **kwargs):
        """Initialize the mixin."""
        super().__init__(*args, **kwargs)

        self.dev = os.environ.get('DEVICE', 'cpu')

        if 'PADDLE_PDX_CACHE_HOME' in os.environ:
            _from = 'PADDLE_PDX_CACHE_HOME'
            self.basedir = Path(os.environ.get('PADDLE_PDX_CACHE_HOME'))
        if 'PADDLEOCR_PREFIX' in os.environ:
            _from = 'PADDLEOCR_PREFIX'
            self.basedir = Path(os.environ.get('PADDLEOCR_PREFIX'))
        elif 'OCT_BASE_DIR' in os.environ:
            _from = 'OCT_BASE_DIR'
            self.basedir = Path(os.environ.get('OCT_BASE_DIR')) / 'models' / 'paddleocr'
        else:
            raise ValueError('No PADDLE_PDX_CACHE_HOME, PADDLEOCR_PREFIX or OCT_BASE_DIR environment variable found.')
        logger.info(f'Taking model dir from { _from }: {self.basedir}')
        self.basedir.mkdir(exist_ok=True, parents=True)

        os.environ['PADDLE_PDX_CACHE_HOME'] = str(self.basedir)

        # This needs to be loaded after `PADDLE_PDX_CACHE_HOME` is set.
        global LOADED
        global PaddleOCR
        if not LOADED:
            PaddleOCR = importlib.import_module('paddleocr').PaddleOCR
            LOADED = True

# class PaddleBOXModel(m.OCRBoxModel, EnvMixin):
#     """OCRtranslate plugin to allow usage of easyocr for box detection."""
#     ALLOWED_OPTIONS = {
#         **m.OCRBoxModel.ALLOWED_OPTIONS,
#         'margin_x_percent': {
#             'type': float,
#             'default':  0.01,
#             'description': 'Percentage of the image width to use as margin for merging boxes during detection.',
#         },
#         'margin_y_percent': {
#             'type': float,
#             'default':  0.01,
#             'description': 'Percentage of the image height to use as margin for merging boxes during detection.',
#         },
#     }
#     class Meta: # pylint: disable=missing-class-docstring
#         proxy = True

#     def __init__(self, *args, **kwargs):
#         """Initialize the model."""
#         self.reader = None
#         super().__init__(*args, **kwargs)

#     def load(self):
#         """Load the model into memory."""
#         logger.debug('Loading PaddleOCR BOX model (using "ch" language)')
#         lang = 'ch'
#         self.reader = PaddleOCR(
#             lang=lang,
#             use_textline_orientation=True,
#             )

#     def unload(self) -> None:
#         """Unload the model from memory."""
#         logger.debug('Unloading PaddleOCR model')
#         if self.reader is not None:
#             del self.reader
#             self.reader = None


#     @staticmethod
#     def trim_overlapping_bboxes(
#             bboxes: list[tuple[int, int, int, int]],
#             ) -> list[tuple[int, int, int, int]]:
#         """Trim overlapping bounding boxes with the condition that the center of the box is inside the other box.

#         Args:
#             bboxes (list[tuple[int, int, int, int]], optional): List of bounding boxes in lrbt format.

#         Returns:
#             list[tuple[int, int, int, int]]: List of trimmed bounding boxes in lrbt format.
#         """
#         bboxes = np.array(bboxes).reshape(-1,4)
#         num_bboxes = bboxes.shape[0]
#         centers = np.empty((num_bboxes, 2), dtype=np.float32)
#         centers[:, 0] = (bboxes[:, 0] + bboxes[:, 1]) / 2
#         centers[:, 1] = (bboxes[:, 2] + bboxes[:, 3]) / 2

#         # Sort by area
#         areas = (bboxes[:, 1] - bboxes[:, 0]) * (bboxes[:, 3] - bboxes[:, 2])
#         sorted_indices = np.argsort(areas)[::-1]

#         keep = []
#         for inner in sorted_indices:
#             # Check if center is inside another box
#             for outer in keep:
#                 if (bboxes[outer, 0] <= centers[inner, 0] <= bboxes[outer, 1] and
#                         bboxes[outer, 2] <= centers[inner, 1] <= bboxes[outer, 3]):
#                     break
#             else:
#                 keep.append(inner)

#         return bboxes[sorted(keep)].tolist()

#     @staticmethod
#     def intersections(
#             bboxes: Iterable[tuple[int, int, int, int]],
#             margin_x: int = 5, margin_y: int = 5
#         ) -> list[set[int]]:
#         """Determine the intersections between a list of bounding boxes.

#         Args:
#             bboxes (Iterable[tuple[int, int, int, int]]): List of bounding boxes in lrbt format.
#             margin_x (int, optional): Number of extra pixels outside of the boxes that define an intersection
#                 in the X axis. Defaults to 5.
#             margin_y (int, optional): Number of extra pixels outside of the boxes that define an intersection

#         Returns:
#             list[set[int]]: List of sets of indexes of the boxes that intersect.
#         """
#         res = []

#         for i,(l1,r1,b1,t1) in enumerate(bboxes):
#             l1 -= margin_x
#             r1 += margin_x
#             b1 -= margin_y
#             t1 += margin_y

#             for j,(l2,r2,b2,t2) in enumerate(bboxes):
#                 if i == j:
#                     continue

#                 if l1 >= r2 or r1 <= l2 or b1 >= t2 or t1 <= b2:
#                     continue

#                 for ptr in res:
#                     if i in ptr or j in ptr:
#                         break
#                 else:
#                     ptr = set()
#                     res.append(ptr)

#                 ptr.add(i)
#                 ptr.add(j)

#         # Merge intersections. Needed depending on ordering of boxes eg  1-4-3-2 would result in [{1,4,3},{2,3}]
#         # instead of [{1,4,3,2}]
#         torm = []
#         for i,ptr1 in enumerate(res):
#             if ptr1 in torm:
#                 continue
#             for ptr2 in res[i+1:]:
#                 if ptr1.intersection(ptr2):
#                     ptr1.update(ptr2)
#                     torm.append(ptr2)

#         for ptr in torm:
#             res.remove(ptr)

#         return res

#     @staticmethod
#     def merge_bboxes(
#             bboxes: Iterable[tuple[int, int, int, int]],
#             margin_x: int = 5, margin_y: int = 5
#         ) -> list[tuple[int, int, int, int]]:
#         """Merge a list of intersecting bounding boxes. All intersecting boxes are merged into a single box.

#         Args:
#             bboxes (Iterable[Iterable[int, int, int, int]]): Iterable of bounding boxes in lrbt format.
#             margin_x (int, optional): Number of extra pixels outside of the boxes that define an intersection
#                 in the X axis. Defaults to 5.
#             margin_y (int, optional): Number of extra pixels outside of the boxes that define an intersection
#                 in the Y axis. Defaults to 5.

#         Returns:
#             list[tuple[int, int, int, int]]: List of merged bounding boxes in lbrt format (!!NOTE the lrbt -> lbrt).
#         """
#         res = []
#         bboxes = np.array(bboxes)
#         inters = PaddleBOXModel.intersections(bboxes, margin_x, margin_y)

#         lst = set(range(len(bboxes)))

#         torm = set()
#         for app in inters:
#             app = list(app)
#             data = bboxes[app].reshape(-1,4)
#             l = data[:,0].min()
#             r = data[:,1].max()
#             b = data[:,2].min()
#             t = data[:,3].max()

#             ptr = {}
#             ptr['merged'] = [l,b,r,t]
#             ptr['single'] = [bboxes[i] for i in app]
#             ptr['single'] = [[l,b,r,t] for l,r,b,t in ptr['single']]
#             res.append(ptr)

#             torm = torm.union(app)

#         for i in lst.difference(torm):
#             l,r,b,t = bboxes[i]
#             # res.append([l,b,r,t])
#             ptr = {}
#             ptr['merged'] = [l,b,r,t]
#             ptr['single'] = [[l,b,r,t]]
#             res.append(ptr)

#         return res

#     def _box_detection(
#             self,
#             image: Image.Image, options: dict = None
#             ) -> list[tuple[int, int, int, int]]:
#         """Perform box OCR on an image.

#         Args:
#             image (Image.Image): A Pillow image on which to perform OCR.
#             options (dict, optional): A dictionary of options.

#         Raises:
#             NotImplementedError: The type of model specified is not implemented.

#         Returns:
#             list[tuple[int, int, int, int]]: A list of bounding boxes in lrbt format.
#         """
#         if options is None:
#             options = {}

#         mxp = float(options.get('margin_x_percent', 0.01))
#         myp = float(options.get('margin_y_percent', 0.01))

#         X,Y = image.size

#         margin_x = int(X * mxp)
#         margin_y = int(Y * myp)

#         image = image.convert('RGB')

#         result = self.reader.predict(
#             np.array(image),
#             use_doc_orientation_classify=True,
#             # rec=False
#             )#[0]
#         def print_recursive(result, level=1):
#             """Print the result recursively."""
#             for k, v in result.items():
#                 if isinstance(v, dict):
#                     print('|  ' * level + f'{k}:')
#                     print_recursive(v, level + 1)
#                 elif isinstance(v, list):
#                     print('|  ' * level + f'{k}: list<{len(v)}> {str(v)[:50]}')
#                 elif isinstance(v, np.ndarray):
#                     print('|  ' * level + f'{k}: array<{v.shape}>')
#                 else:
#                     print('|  ' * level + f'{k}: {str(v)[:50]}')
#         for idx, res in enumerate(result):
#             logger.debug(f'RESULTS #{idx} --------------')
#             print_recursive(res)
#         result = result[0]
#         result = result or {}

#         # bboxes = []
#         # for res in result.get('rec_boxes', []):
#         #     print(f'RESULT BOX: {list(res)}')
#         #     b, l, t, r = np.array(res)

#         bboxes = []
#         for res in result.get('rec_polys', []):
#             box = np.array(res)
#             b = box[:, 0].min()
#             t = box[:, 0].max()
#             l = box[:, 1].min()
#             r = box[:, 1].max()
#             print(f'RESULT BOX: {(l, r, b, t)}')
#             bboxes.append((l, r, b, t))
#         bboxes = self.trim_overlapping_bboxes(bboxes)

#         bboxes = self.merge_bboxes(bboxes, margin_x, margin_y)

#         return bboxes

class PaddleOCRModel(m.OCRModel, EnvMixin):
    """OCRtranslate plugin to allow loading of PaddleOCR as text OCR."""
    class Meta: # pylint: disable=missing-class-docstring
        proxy = True

    def __init__(self, *args, **kwargs):
        """Initialize the model."""
        self.lang = None
        self.reader = None
        super().__init__(*args, **kwargs)

    def load(self):
        """Load the model into memory."""
        logger.debug('Loading PaddleOCR model (nothing to do here)')

    def unload(self) -> None:
        """Unload the model from memory."""
        logger.debug('Unloading PaddleOCR model')
        self.lang = None
        if self.reader is not None:
            del self.reader
            self.reader = None

    def _ocr(
            self,
            img: Image.Image, lang: str = None, options: dict = None
            ) -> str:
        """Perform OCR on an image.

        Args:
            img (Image.Image):  A Pillow image on which to perform OCR.
            lang (str, optional): The language to use for OCR. (Not every model will use this)
            bbox (tuple[int, int, int, int], optional): The bounding box of the text on the image in lbrt format.
            options (dict, optional): A dictionary of options to pass to the OCR model.

        Raises:
            TypeError: If img is not a Pillow image.

        Returns:
            str: The text extracted from the image.
        """

        if lang != self.lang:
            self.lang = lang
            self.reader = PaddleOCR(
                use_angle_cls=True, lang=lang,
                )

        result = self.reader.predict(
            np.array(img),
            use_doc_orientation_classify=True,
            )

        # def print_recursive(result, level=1):
        #     """Print the result recursively."""
        #     for k, v in result.items():
        #         if isinstance(v, dict):
        #             print('|  ' * level + f'{k}:')
        #             print_recursive(v, level + 1)
        #         elif isinstance(v, np.ndarray):
        #             print('|  ' * level + f'{k}: array<{v.shape}>')
        #         else:
        #             print('|  ' * level + f'{k}: {str(v)[:50]}')
        # for idx, res in enumerate(result):
        #     print(f'RESULTS #{idx} --------------')
        #     print_recursive(res)
        result = result[0]
        result = result or {}

        generated_text = result.get('rec_texts', [])
        generated_text = ' '.join(generated_text)

        return generated_text
