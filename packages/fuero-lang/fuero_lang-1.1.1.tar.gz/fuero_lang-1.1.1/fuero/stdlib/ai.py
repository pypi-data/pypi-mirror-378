"""
ai utilities for fuero
provides machine learning and ai functionality
"""

import json
import requests
from typing import Dict, List, Any, Optional, Union
import base64
import os


class Ai:
    """ai and machine learning utilities"""
    
    def __init__(self):
        self.api_keys = {}
        self.default_models = {
            'text_generation': 'gpt-3.5-turbo',
            'text_embedding': 'text-embedding-ada-002',
            'image_generation': 'dall-e-3',
            'speech_to_text': 'whisper-1',
            'text_to_speech': 'tts-1'
        }
    
    # API Key management
    def set_api_key(self, service: str, api_key: str):
        """Set API key for AI service"""
        self.api_keys[service] = api_key
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for service"""
        return self.api_keys.get(service)
    
    # Text Generation
    def generate_text(self, prompt: str, model: Optional[str] = None, 
                     max_tokens: int = 150, temperature: float = 0.7,
                     service: str = 'openai') -> Dict[str, Any]:
        """Generate text using AI model"""
        if service == 'openai':
            return self._openai_text_generation(prompt, model, max_tokens, temperature)
        else:
            raise ValueError(f"Unsupported service: {service}")
    
    def _openai_text_generation(self, prompt: str, model: Optional[str], 
                               max_tokens: int, temperature: float) -> Dict[str, Any]:
        """OpenAI text generation"""
        api_key = self.get_api_key('openai')
        if not api_key:
            raise ValueError("OpenAI API key not set")
        
        model = model or self.default_models['text_generation']
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': max_tokens,
            'temperature': temperature
        }
        
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                'text': result['choices'][0]['message']['content'],
                'model': model,
                'usage': result.get('usage', {}),
                'finish_reason': result['choices'][0].get('finish_reason')
            }
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request failed: {e}")
    
    def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None,
                       temperature: float = 0.7, service: str = 'openai') -> Dict[str, Any]:
        """Multi-turn chat completion"""
        if service == 'openai':
            return self._openai_chat_completion(messages, model, temperature)
        else:
            raise ValueError(f"Unsupported service: {service}")
    
    def _openai_chat_completion(self, messages: List[Dict[str, str]], 
                               model: Optional[str], temperature: float) -> Dict[str, Any]:
        """OpenAI chat completion"""
        api_key = self.get_api_key('openai')
        if not api_key:
            raise ValueError("OpenAI API key not set")
        
        model = model or self.default_models['text_generation']
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': messages,
            'temperature': temperature
        }
        
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                'message': result['choices'][0]['message'],
                'model': model,
                'usage': result.get('usage', {}),
                'finish_reason': result['choices'][0].get('finish_reason')
            }
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request failed: {e}")
    
    # Text Embeddings
    def get_embeddings(self, texts: Union[str, List[str]], model: Optional[str] = None,
                      service: str = 'openai') -> Dict[str, Any]:
        """Get text embeddings"""
        if service == 'openai':
            return self._openai_embeddings(texts, model)
        else:
            raise ValueError(f"Unsupported service: {service}")
    
    def _openai_embeddings(self, texts: Union[str, List[str]], 
                          model: Optional[str]) -> Dict[str, Any]:
        """OpenAI embeddings"""
        api_key = self.get_api_key('openai')
        if not api_key:
            raise ValueError("OpenAI API key not set")
        
        model = model or self.default_models['text_embedding']
        
        if isinstance(texts, str):
            texts = [texts]
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'input': texts
        }
        
        try:
            response = requests.post(
                'https://api.openai.com/v1/embeddings',
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            embeddings = [item['embedding'] for item in result['data']]
            
            return {
                'embeddings': embeddings[0] if len(embeddings) == 1 else embeddings,
                'model': model,
                'usage': result.get('usage', {})
            }
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request failed: {e}")
    
    # Image Generation
    def generate_image(self, prompt: str, size: str = '1024x1024', 
                      quality: str = 'standard', model: Optional[str] = None,
                      service: str = 'openai') -> Dict[str, Any]:
        """Generate image from text prompt"""
        if service == 'openai':
            return self._openai_image_generation(prompt, size, quality, model)
        else:
            raise ValueError(f"Unsupported service: {service}")
    
    def _openai_image_generation(self, prompt: str, size: str, quality: str,
                                model: Optional[str]) -> Dict[str, Any]:
        """OpenAI image generation"""
        api_key = self.get_api_key('openai')
        if not api_key:
            raise ValueError("OpenAI API key not set")
        
        model = model or self.default_models['image_generation']
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'prompt': prompt,
            'size': size,
            'quality': quality,
            'n': 1
        }
        
        try:
            response = requests.post(
                'https://api.openai.com/v1/images/generations',
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                'url': result['data'][0]['url'],
                'revised_prompt': result['data'][0].get('revised_prompt'),
                'model': model
            }
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request failed: {e}")
    
    # Speech to Text
    def speech_to_text(self, audio_file_path: str, model: Optional[str] = None,
                      language: Optional[str] = None, service: str = 'openai') -> Dict[str, Any]:
        """Convert speech to text"""
        if service == 'openai':
            return self._openai_speech_to_text(audio_file_path, model, language)
        else:
            raise ValueError(f"Unsupported service: {service}")
    
    def _openai_speech_to_text(self, audio_file_path: str, model: Optional[str],
                              language: Optional[str]) -> Dict[str, Any]:
        """OpenAI speech to text (Whisper)"""
        api_key = self.get_api_key('openai')
        if not api_key:
            raise ValueError("OpenAI API key not set")
        
        model = model or self.default_models['speech_to_text']
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        data = {
            'model': model
        }
        
        if language:
            data['language'] = language
        
        try:
            with open(audio_file_path, 'rb') as audio_file:
                files = {
                    'file': audio_file
                }
                
                response = requests.post(
                    'https://api.openai.com/v1/audio/transcriptions',
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=60
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    'text': result['text'],
                    'model': model,
                    'language': result.get('language')
                }
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request failed: {e}")
    
    # Text to Speech
    def text_to_speech(self, text: str, voice: str = 'alloy', model: Optional[str] = None,
                      output_file: Optional[str] = None, service: str = 'openai') -> Dict[str, Any]:
        """Convert text to speech"""
        if service == 'openai':
            return self._openai_text_to_speech(text, voice, model, output_file)
        else:
            raise ValueError(f"Unsupported service: {service}")
    
    def _openai_text_to_speech(self, text: str, voice: str, model: Optional[str],
                              output_file: Optional[str]) -> Dict[str, Any]:
        """OpenAI text to speech"""
        api_key = self.get_api_key('openai')
        if not api_key:
            raise ValueError("OpenAI API key not set")
        
        model = model or self.default_models['text_to_speech']
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'input': text,
            'voice': voice
        }
        
        try:
            response = requests.post(
                'https://api.openai.com/v1/audio/speech',
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            audio_content = response.content
            
            if output_file:
                with open(output_file, 'wb') as f:
                    f.write(audio_content)
                return {
                    'file_path': output_file,
                    'model': model,
                    'voice': voice
                }
            else:
                return {
                    'audio_data': base64.b64encode(audio_content).decode('utf-8'),
                    'model': model,
                    'voice': voice
                }
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request failed: {e}")
    
    # Text Analysis
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text (simple implementation)"""
        # This is a basic implementation - in a real scenario, you'd use a proper ML model
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'happy', 'joy']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'sad', 'angry', 'disappointed', 'frustrated']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text (simple implementation)"""
        import re
        from collections import Counter
        
        # Simple keyword extraction - remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Extract words and filter
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count frequency and return top keywords
        word_counts = Counter(filtered_words)
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """Summarize text (simple extractive summarization)"""
        import re
        from collections import Counter
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            return text
        
        # Simple scoring based on word frequency
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_freq = Counter(words)
        
        # Score sentences
        sentence_scores = []
        for sentence in sentences:
            sentence_words = re.findall(r'\b[a-zA-Z]{3,}\b', sentence.lower())
            score = sum(word_freq[word] for word in sentence_words)
            sentence_scores.append((score, sentence))
        
        # Return top sentences
        top_sentences = sorted(sentence_scores, reverse=True)[:max_sentences]
        top_sentences.sort(key=lambda x: sentences.index(x[1]))  # Maintain original order
        
        return '. '.join(sentence for score, sentence in top_sentences) + '.'
    
    # Utility functions
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same length")
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def find_similar_texts(self, query_embedding: List[float], 
                          text_embeddings: List[List[float]], 
                          texts: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Find most similar texts based on embeddings"""
        similarities = []
        
        for i, embedding in enumerate(text_embeddings):
            similarity = self.cosine_similarity(query_embedding, embedding)
            similarities.append({
                'text': texts[i],
                'similarity': similarity,
                'index': i
            })
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def tokenize_text(self, text: str) -> List[str]:
        """Simple text tokenization"""
        import re
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using Jaccard similarity"""
        tokens1 = set(self.tokenize_text(text1))
        tokens2 = set(self.tokenize_text(text2))
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def get_available_models(self, service: str = 'openai') -> Dict[str, List[str]]:
        """Get available models for a service"""
        if service == 'openai':
            return {
                'text_generation': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
                'text_embedding': ['text-embedding-ada-002', 'text-embedding-3-small', 'text-embedding-3-large'],
                'image_generation': ['dall-e-2', 'dall-e-3'],
                'speech_to_text': ['whisper-1'],
                'text_to_speech': ['tts-1', 'tts-1-hd']
            }
        else:
            return {}
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate number of tokens in text (rough approximation)"""
        # Rough estimation: 1 token ≈ 4 characters for English text
        return len(text) // 4
