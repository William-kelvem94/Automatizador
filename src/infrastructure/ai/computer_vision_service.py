# -*- coding: utf-8 -*-

"""
COMPUTER VISION SERVICE
Sistema de visão computacional para análise de interfaces web
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import base64
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import requests
from datetime import datetime

from ...shared.utils.logger import get_logger
from ...infrastructure.monitoring.metrics_collector import metrics_collector


class ComputerVisionService:
    """Serviço de visão computacional para análise de interfaces"""

    def __init__(self):
        self.logger = get_logger(__name__)

        # Verificar se Tesseract está disponível
        try:
            pytesseract.get_tesseract_version()
            self.ocr_available = True
            self.logger.info("Tesseract OCR disponível")
        except Exception:
            self.ocr_available = False
            self.logger.warning("Tesseract OCR não disponível - OCR desabilitado")

        # Modelos carregados (cache)
        self.models_cache = {}

        # Estatísticas
        self.stats = {
            'images_processed': 0,
            'text_extracted': 0,
            'elements_detected': 0,
            'errors': 0
        }

    def analyze_screenshot(self, image_data: bytes, analysis_type: str = "full") -> Dict[str, Any]:
        """
        Analisar screenshot de interface web

        Args:
            image_data: Dados binários da imagem
            analysis_type: Tipo de análise ('full', 'text', 'elements', 'layout')

        Returns:
            Resultado da análise
        """
        start_time = time.time()

        try:
            self.stats['images_processed'] += 1

            # Carregar imagem
            image = self._load_image(image_data)
            if image is None:
                return {'success': False, 'error': 'Falha ao carregar imagem'}

            result = {
                'success': True,
                'image_info': self._get_image_info(image),
                'analysis_type': analysis_type,
                'timestamp': datetime.now().isoformat()
            }

            # Análises específicas
            if analysis_type in ['full', 'text']:
                result['text_analysis'] = self._extract_text(image)

            if analysis_type in ['full', 'elements']:
                result['element_detection'] = self._detect_ui_elements(image)

            if analysis_type in ['full', 'layout']:
                result['layout_analysis'] = self._analyze_layout(image)

            # Métricas de performance
            result['processing_time'] = time.time() - start_time
            metrics_collector.observe_histogram(
                'automator_cv_processing_time_seconds',
                result['processing_time'],
                {'analysis_type': analysis_type}
            )

            return result

        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"Erro na análise de screenshot: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }

    def _load_image(self, image_data: bytes) -> Optional[np.ndarray]:
        """Carregar imagem de dados binários"""
        try:
            # Converter para array numpy
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is None:
                # Tentar com PIL
                pil_image = Image.open(io.BytesIO(image_data))
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

            return image

        except Exception as e:
            self.logger.error(f"Erro ao carregar imagem: {e}")
            return None

    def _get_image_info(self, image: np.ndarray) -> Dict[str, Any]:
        """Obter informações básicas da imagem"""
        height, width = image.shape[:2]

        return {
            'width': width,
            'height': height,
            'channels': image.shape[2] if len(image.shape) > 2 else 1,
            'size_bytes': image.nbytes,
            'aspect_ratio': width / height if height > 0 else 0
        }

    def _extract_text(self, image: np.ndarray) -> Dict[str, Any]:
        """Extrair texto da imagem usando OCR"""
        if not self.ocr_available:
            return {
                'available': False,
                'text': '',
                'confidence': 0.0
            }

        try:
            # Pré-processamento para melhor OCR
            processed_image = self._preprocess_for_ocr(image)

            # Extrair texto
            text_data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)

            # Filtrar texto válido
            valid_texts = []
            confidences = []

            for i, confidence in enumerate(text_data['conf']):
                if int(confidence) > 30:  # Confiança mínima
                    text = text_data['text'][i].strip()
                    if text and len(text) > 1:
                        valid_texts.append({
                            'text': text,
                            'confidence': float(confidence),
                            'bbox': {
                                'x': text_data['left'][i],
                                'y': text_data['top'][i],
                                'width': text_data['width'][i],
                                'height': text_data['height'][i]
                            }
                        })
                        confidences.append(float(confidence))

            # Estatísticas
            avg_confidence = np.mean(confidences) if confidences else 0.0
            full_text = ' '.join([item['text'] for item in valid_texts])

            self.stats['text_extracted'] += len(valid_texts)

            return {
                'available': True,
                'text_count': len(valid_texts),
                'average_confidence': avg_confidence,
                'full_text': full_text,
                'text_elements': valid_texts
            }

        except Exception as e:
            self.logger.error(f"Erro na extração de texto: {e}")
            return {
                'available': True,
                'error': str(e),
                'text_count': 0,
                'average_confidence': 0.0
            }

    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Pré-processar imagem para melhor OCR"""
        try:
            # Converter para grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Aplicar threshold
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Redução de ruído
            denoised = cv2.medianBlur(thresh, 3)

            return denoised

        except Exception:
            # Retornar imagem original se pré-processamento falhar
            return image

    def _detect_ui_elements(self, image: np.ndarray) -> Dict[str, Any]:
        """Detectar elementos de UI na imagem"""
        try:
            elements = {
                'buttons': [],
                'inputs': [],
                'text_fields': [],
                'images': [],
                'links': []
            }

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Edge detection
            edges = cv2.Canny(gray, 50, 150)

            # Find contours (potential UI elements)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 100:  # Too small
                    continue

                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)

                # Classify element based on shape and size
                aspect_ratio = w / h if h > 0 else 0

                element = {
                    'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                    'area': area,
                    'aspect_ratio': aspect_ratio
                }

                # Simple classification based on aspect ratio and size
                if 0.5 < aspect_ratio < 2.0 and 500 < area < 10000:
                    # Likely a button
                    elements['buttons'].append(element)
                elif aspect_ratio > 3.0 and area > 200:
                    # Likely an input field
                    elements['inputs'].append(element)
                elif 1.0 < aspect_ratio < 3.0 and area > 1000:
                    # Likely a text field or image
                    # Additional check for text content
                    roi = gray[y:y+h, x:x+w]
                    if self._is_text_region(roi):
                        elements['text_fields'].append(element)
                    else:
                        elements['images'].append(element)

            self.stats['elements_detected'] += sum(len(v) for v in elements.values())

            return {
                'total_elements': sum(len(v) for v in elements.values()),
                'elements': elements,
                'detection_method': 'contour_analysis'
            }

        except Exception as e:
            self.logger.error(f"Erro na detecção de elementos: {e}")
            return {
                'total_elements': 0,
                'elements': {},
                'error': str(e)
            }

    def _is_text_region(self, roi: np.ndarray) -> bool:
        """Verificar se uma região contém texto"""
        try:
            if not self.ocr_available:
                return False

            # Simple heuristic: check if OCR finds text
            text = pytesseract.image_to_string(roi, config='--psm 6')
            return len(text.strip()) > 3  # At least 3 characters

        except Exception:
            return False

    def _analyze_layout(self, image: np.ndarray) -> Dict[str, Any]:
        """Analisar layout da página"""
        try:
            height, width = image.shape[:2]

            # Detectar áreas principais (header, content, footer)
            layout_regions = {
                'header': {'y': 0, 'height': int(height * 0.15)},
                'content': {'y': int(height * 0.15), 'height': int(height * 0.7)},
                'footer': {'y': int(height * 0.85), 'height': int(height * 0.15)}
            }

            # Análise de cores dominantes
            pixels = image.reshape(-1, 3)
            pixels = pixels[np.random.choice(pixels.shape[0], min(10000, pixels.shape[0]), replace=False)]
            dominant_colors = self._find_dominant_colors(pixels, k=5)

            # Detectar elementos estruturais
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            lines = cv2.HoughLinesP(gray, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)

            structural_elements = len(lines) if lines is not None else 0

            return {
                'dimensions': {'width': width, 'height': height},
                'layout_regions': layout_regions,
                'dominant_colors': dominant_colors,
                'structural_elements': structural_elements,
                'estimated_layout': self._classify_layout(layout_regions, structural_elements)
            }

        except Exception as e:
            self.logger.error(f"Erro na análise de layout: {e}")
            return {'error': str(e)}

    def _find_dominant_colors(self, pixels: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Encontrar cores dominantes usando k-means"""
        try:
            from sklearn.cluster import KMeans

            kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
            kmeans.fit(pixels)

            colors = []
            for center in kmeans.cluster_centers_:
                colors.append({
                    'rgb': [int(c) for c in center],
                    'hex': '#{:02x}{:02x}{:02x}'.format(int(center[0]), int(center[1]), int(center[2]))
                })

            return colors

        except ImportError:
            # Fallback sem sklearn
            return [{'rgb': [128, 128, 128], 'hex': '#808080', 'note': 'sklearn not available'}]
        except Exception as e:
            self.logger.debug(f"Erro ao encontrar cores dominantes: {e}")
            return []

    def _classify_layout(self, regions: Dict, structural_elements: int) -> str:
        """Classificar tipo de layout"""
        # Simple classification based on heuristics
        if structural_elements > 20:
            return "complex_grid"
        elif regions['content']['height'] > regions['header']['height'] * 3:
            return "content_heavy"
        else:
            return "standard_webpage"

    def compare_screenshots(self, image1_data: bytes, image2_data: bytes) -> Dict[str, Any]:
        """Comparar duas screenshots para detectar diferenças"""
        try:
            img1 = self._load_image(image1_data)
            img2 = self._load_image(image2_data)

            if img1 is None or img2 is None:
                return {'success': False, 'error': 'Falha ao carregar imagens'}

            # Resize para mesmo tamanho se necessário
            if img1.shape != img2.shape:
                height = min(img1.shape[0], img2.shape[0])
                width = min(img1.shape[1], img2.shape[1])
                img1 = cv2.resize(img1, (width, height))
                img2 = cv2.resize(img2, (width, height))

            # Calcular diferença
            diff = cv2.absdiff(img1, img2)
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

            # Threshold para destacar diferenças
            _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)

            # Calcular porcentagem de diferença
            total_pixels = thresh.size
            diff_pixels = cv2.countNonZero(thresh)
            diff_percentage = (diff_pixels / total_pixels) * 100

            # Encontrar regiões de diferença
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            diff_regions = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Ignorar diferenças muito pequenas
                    x, y, w, h = cv2.boundingRect(contour)
                    diff_regions.append({
                        'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                        'area': area
                    })

            return {
                'success': True,
                'difference_percentage': diff_percentage,
                'total_diff_regions': len(diff_regions),
                'diff_regions': diff_regions[:10],  # Limitar para performance
                'similarity_score': 100 - diff_percentage
            }

        except Exception as e:
            self.logger.error(f"Erro na comparação de screenshots: {e}")
            return {'success': False, 'error': str(e)}

    def extract_form_elements(self, image_data: bytes) -> Dict[str, Any]:
        """Extrair elementos de formulário da screenshot"""
        try:
            image = self._load_image(image_data)
            if image is None:
                return {'success': False, 'error': 'Falha ao carregar imagem'}

            # Detectar elementos retangulares (potenciais campos de formulário)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(blurred, 50, 150)

            contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            form_elements = []
            height, width = image.shape[:2]

            for contour in contours:
                area = cv2.contourArea(contour)
                if 500 < area < 50000:  # Tamanho típico de campos de formulário
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0

                    # Filtrar formas retangulares
                    if 2 < aspect_ratio < 20:  # Campos alongados horizontalmente
                        # Verificar se parece com um campo de entrada
                        roi = gray[y:y+h, x:x+w]

                        # Análise de cor (campos geralmente têm fundo branco/cinza claro)
                        mean_color = cv2.mean(roi)[0]

                        if mean_color > 150:  # Fundo claro
                            form_elements.append({
                                'type': 'input_field',
                                'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                                'confidence': 0.7,
                                'aspect_ratio': aspect_ratio
                            })

            return {
                'success': True,
                'form_elements_found': len(form_elements),
                'elements': form_elements
            }

        except Exception as e:
            self.logger.error(f"Erro na extração de elementos de formulário: {e}")
            return {'success': False, 'error': str(e)}

    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do serviço"""
        return dict(self.stats)

    def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde do serviço"""
        try:
            return {
                'status': 'healthy',
                'ocr_available': self.ocr_available,
                'opencv_version': cv2.__version__,
                'stats': self.get_stats()
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Instância global
cv_service = ComputerVisionService()


# Funções utilitárias
def analyze_webpage_screenshot(image_data: bytes) -> Dict[str, Any]:
    """Analisar screenshot de página web"""
    return cv_service.analyze_screenshot(image_data, "full")


def extract_text_from_image(image_data: bytes) -> str:
    """Extrair texto de imagem"""
    result = cv_service.analyze_screenshot(image_data, "text")
    return result.get('text_analysis', {}).get('full_text', '') if result['success'] else ''


def compare_ui_screenshots(before: bytes, after: bytes) -> Dict[str, Any]:
    """Comparar screenshots de interface"""
    return cv_service.compare_screenshots(before, after)
