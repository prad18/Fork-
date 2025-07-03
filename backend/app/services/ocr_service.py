from paddleocr import PaddleOCR
from PIL import Image
import fitz
import os

class OCRService:
    def __init__(self):
        print("🔄 Initializing PaddleOCR...")
        try:
            # Re-enable angle classification to see if it helps with text structure
            self.ocr = PaddleOCR(
                use_angle_cls=True,  # Re-enable for better text structure
                lang='en'
            )
            print("✅ PaddleOCR initialized successfully (with angle classification)")
            
        except Exception as e:
            print(f"❌ PaddleOCR initialization failed: {e}")
            self.ocr = None
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from image or PDF file using PaddleOCR"""
        
        # Try to initialize OCR if it failed during __init__
        if not self.ocr:
            print("🔄 Attempting to re-initialize PaddleOCR...")
            try:
                self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
                print("✅ PaddleOCR re-initialized successfully")
            except Exception as e:
                print(f"❌ Failed to re-initialize PaddleOCR: {e}")
                return f"OCR service initialization failed: {str(e)}"
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                return self._extract_text_from_pdf(file_path)
            else:
                return self._extract_text_from_image(file_path)
        except Exception as e:
            error_msg = f"OCR Error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _extract_text_from_image(self, file_path: str) -> str:
        """Extract text from image file - optimized for speed"""
        try:
            # Optimize image for faster processing
            image = Image.open(file_path)
            
            # Resize large images for faster processing (huge speed boost)
            max_size = 1920  # Max width/height
            if image.width > max_size or image.height > max_size:
                ratio = min(max_size / image.width, max_size / image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                
                # Save optimized image temporarily
                temp_path = file_path.replace('.', '_optimized.')
                image.save(temp_path, optimize=True, quality=85)
                file_path = temp_path
            else:
                temp_path = None
            
            # Run OCR
            result = self.ocr.ocr(file_path)
            
            # Clean up temp file if created
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            
            if not result or not result[0]:
                return ""
            
            # Convert PaddleOCR result to structured text
            structured_text = self._paddle_result_to_structured_text(result[0])
            
            print(f"✅ PaddleOCR extracted {len(structured_text)} characters from image")
            return structured_text
            
        except Exception as e:
            print(f"Image OCR Error: {str(e)}")
            return ""
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            doc = fitz.open(file_path)
            all_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Try to extract text directly first
                page_text = page.get_text()
                
                if page_text.strip() and len(page_text.strip()) > 50:
                    # If text is extractable and substantial, use it
                    all_text += page_text + "\n"
                else:
                    # If no text or poor quality, use PaddleOCR on the page image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Higher resolution
                    img_data = pix.tobytes("png")
                    
                    # Save to temporary file for PaddleOCR
                    temp_path = f"temp_page_{page_num}.png"
                    with open(temp_path, "wb") as f:
                        f.write(img_data)
                    
                    try:
                        result = self.ocr.ocr(temp_path)
                        if result and result[0]:
                            ocr_text = self._paddle_result_to_structured_text(result[0])
                            all_text += ocr_text + "\n"
                    finally:
                        # Clean up temp file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
            
            doc.close()
            print(f"✅ PaddleOCR extracted {len(all_text)} characters from PDF")
            return all_text.strip()
            
        except Exception as e:
            print(f"PDF OCR Error: {str(e)}")
            return ""
    
    def _paddle_result_to_structured_text(self, ocr_result) -> str:
        """Convert PaddleOCR result to structured text preserving table layout"""
        
        if not ocr_result:
            return ""
        
        # Handle OCRResult object as dictionary-like object
        try:
            # Access as dictionary keys (not attributes)
            if 'rec_texts' in ocr_result and 'rec_polys' in ocr_result:
                texts = ocr_result['rec_texts']
                polys = ocr_result['rec_polys']
                scores = ocr_result.get('rec_scores', [1.0] * len(texts))
                
                if not texts:
                    return ""
                
                # Create structured data similar to old format
                structured_data = []
                for i, (text, poly, score) in enumerate(zip(texts, polys, scores)):
                    try:
                        # Convert poly to bounding box format
                        if len(poly) >= 4:
                            bbox = poly  # Already in correct format
                        else:
                            continue
                            
                        structured_data.append([bbox, [text, score]])
                    except Exception as e:
                        continue
                
                # Process with the structured data
                return self._process_structured_data(structured_data)
        except Exception as e:
            pass
        
        # Handle old list format (fallback)
        if isinstance(ocr_result, list):
            return self._process_structured_data(ocr_result)
        
        # Last resort: try to get text any way possible
        try:
            # Try accessing as dictionary
            if hasattr(ocr_result, 'get'):
                texts = ocr_result.get('rec_texts', [])
                if texts:
                    return '\n'.join([str(text) for text in texts if text and str(text).strip()])
        except Exception:
            pass
        
        return ""
    
    def _process_structured_data(self, structured_data: list) -> str:
        """Process structured OCR data into readable text"""
        
        # Group text boxes by their vertical position (rows)
        rows = {}
        
        for line in structured_data:
            try:
                if len(line) >= 2:
                    bbox = line[0]  # Bounding box coordinates
                    text_info = line[1]  # Text information
                    
                    # Handle different text info formats
                    if isinstance(text_info, list) and len(text_info) >= 2:
                        text = text_info[0]  # Extracted text
                        confidence = text_info[1]  # Confidence score
                    elif isinstance(text_info, str):
                        text = text_info
                        confidence = 1.0  # Default confidence
                    else:
                        print(f"🔍 Unexpected text_info format: {text_info}")
                        continue
                    
                    # Skip low confidence detections
                    if confidence < 0.5:
                        continue
                    
                    # Calculate row position (average y-coordinate)
                    y_coords = [point[1] for point in bbox]
                    row_y = sum(y_coords) / len(y_coords)
                    
                    # Group by row (with some tolerance for alignment)
                    row_key = round(row_y / 10) * 10  # Group within 10 pixel tolerance
                    
                    if row_key not in rows:
                        rows[row_key] = []
                    
                    # Calculate x position for column ordering
                    x_coords = [point[0] for point in bbox]
                    col_x = sum(x_coords) / len(x_coords)
                    
                    rows[row_key].append({
                        'text': text,
                        'x': col_x,
                        'confidence': confidence
                    })
                    
            except Exception as e:
                print(f"🔍 Error processing OCR line {line}: {e}")
                continue
        
        # Build structured text
        structured_lines = []
        
        for row_y in sorted(rows.keys()):
            # Sort columns by x position
            columns = sorted(rows[row_y], key=lambda x: x['x'])
            
            # Join columns with appropriate spacing
            row_text = ""
            last_x = 0
            
            for col in columns:
                # Add spacing based on distance between columns
                if last_x > 0:
                    x_gap = col['x'] - last_x
                    if x_gap > 100:  # Large gap, likely new column
                        row_text += "    "  # Tab-like spacing
                    elif x_gap > 50:  # Medium gap
                        row_text += "  "   # Double space
                    else:
                        row_text += " "    # Single space
                
                row_text += col['text']
                last_x = col['x'] + len(col['text']) * 10  # Estimate text width
            
            structured_lines.append(row_text.strip())
        
        # Join all lines
        final_text = '\n'.join(line for line in structured_lines if line.strip())
        
        return final_text
