"""
Search APIs for interacting with SearchTruth.com
"""
import re
import html
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SearchTruthAPI:
    """API wrapper for SearchTruth.com functionality"""
    
    def __init__(self, timeout=10, user_agent=None):
        self.timeout = timeout
        self.headers = {
            'User-Agent': user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def search_quran(self, keyword: str, chapter: str = "", translator: str = "2", max_results: int = 5) -> List[str]:
        """Search Quran verses using SearchTruth.com"""
        try:
            url = "https://www.searchtruth.com/search.php"
            params = {
                'keyword': keyword,
                'chapter': chapter,
                'translator': translator
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Extract results using multiple strategies
            result_selectors = [
                'div[style*="margin"]',
                'table[width="100%"]',
                '.search_result',
                '.verse_div'
            ]
            
            for selector in result_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements[:max_results]:
                        text = element.get_text(strip=True, separator=' ')
                        if text and len(text) > 20 and keyword.lower() in text.lower():
                            text = self._clean_text(text)
                            results.append(text[:500])
                    if results:
                        break
            
            if not results:
                # Fallback: search in all text
                all_text = soup.get_text()
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                
                keyword_lower = keyword.lower()
                for line in lines:
                    if keyword_lower in line.lower() and len(line) > 30:
                        clean_line = self._clean_text(line)
                        if clean_line not in results:
                            results.append(clean_line[:500])
                            if len(results) >= max_results:
                                break
            
            return results if results else [f"No Quran verses found containing '{keyword}'"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Quran search request error: {e}")
            return ["Unable to search Quran at the moment. Please try again later."]
        except Exception as e:
            logger.error(f"Quran search error: {e}")
            return ["Error processing Quran search. Please try again."]
    
    def search_hadith(self, keyword: str, collection: str = "1", max_results: int = 5) -> List[str]:
        """Search Hadith using SearchTruth.com"""
        try:
            url = "https://www.searchtruth.com/searchHadith.php"
            params = {
                'keyword': keyword,
                'translator': collection
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Try different selectors for hadith results
            selectors = [
                'div[style*="margin"]',
                'table[border="0"]',
                '.hadith_result',
                'tr[bgcolor]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements[:max_results]:
                        text = element.get_text(strip=True, separator=' ')
                        if text and len(text) > 30 and keyword.lower() in text.lower():
                            text = self._clean_text(text)
                            results.append(text[:600])
                    if results:
                        break
            
            if not results:
                # Alternative extraction
                all_text = soup.get_text()
                paragraphs = [p.strip() for p in all_text.split('\n\n') if p.strip()]
                
                keyword_lower = keyword.lower()
                for para in paragraphs:
                    if keyword_lower in para.lower() and len(para) > 50:
                        clean_para = self._clean_text(para)
                        results.append(clean_para[:600])
                        if len(results) >= max_results:
                            break
            
            return results if results else [f"No hadith found containing '{keyword}'"]
            
        except Exception as e:
            logger.error(f"Hadith search error: {e}")
            return ["Unable to search Hadith at the moment. Please try again later."]
    
    def search_dictionary(self, word: str, word_option: str = "1", max_results: int = 8) -> List[str]:
        """Search English-Arabic dictionary"""
        try:
            url = "https://www.searchtruth.com/dictionary/arabic_english_dictionary.php"
            params = {
                'word': word,
                'word_option': word_option
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Extract dictionary entries
            entries = soup.find_all('tr', bgcolor=True)
            
            for entry in entries[:max_results]:
                text = entry.get_text(strip=True, separator=' | ')
                if text and len(text) > 10:
                    text = self._clean_text(text)
                    results.append(text[:400])
            
            if not results:
                # Try alternative extraction
                tables = soup.find_all('table', width=lambda x: x and x == '100%')
                for table in tables:
                    text = table.get_text(strip=True, separator=' | ')
                    if word.lower() in text.lower() and len(text) > 20:
                        results.append(text[:400])
                        if len(results) >= max_results:
                            break
            
            return results if results else [f"No dictionary entries found for '{word}'"]
            
        except Exception as e:
            logger.error(f"Dictionary search error: {e}")
            return ["Unable to access dictionary at the moment. Please try again later."]
    
    def get_prayer_cities(self, country: str) -> Dict:
        """Get list of cities for a country"""
        try:
            country_url = country.replace(' ', '_').lower()
            url = f"https://www.searchtruth.com/prayertimes/city.php?country={country_url}"
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            cities = []
            
            # Extract city links
            city_links = soup.find_all('a', href=lambda x: x and 'prayertimes' in x and 'city=' in x)
            
            for link in city_links:
                city_name = link.get_text(strip=True)
                if city_name and city_name not in cities:
                    cities.append(city_name)
            
            return {
                "country": country,
                "available_cities": cities[:20],
                "total_cities": len(cities)
            }
            
        except Exception as e:
            logger.error(f"Prayer cities error: {e}")
            return {
                "error": f"Unable to get cities for {country}",
                "suggestion": "Please try a different country or check the country name."
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text"""
        text = re.sub(r'\s+', ' ', text)
        text = html.unescape(text)
        return text.strip()