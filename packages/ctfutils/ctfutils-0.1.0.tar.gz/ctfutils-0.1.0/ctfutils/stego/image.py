"""Image steganography utilities."""

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from ..exceptions import SteganographyError


class ImageSteganography:
    """Image steganography utilities using LSB method."""
    
    def __init__(self):
        """Initialize image steganography handler."""
        if not PIL_AVAILABLE:
            raise SteganographyError("Pillow library required for image steganography")
    
    def hide_text_lsb(self, image_path: str, secret_text: str, output_path: str) -> None:
        """
        Hide text in image using LSB steganography.
        
        Args:
            image_path: Path to cover image
            secret_text: Text to hide
            output_path: Path to save stego image
        """
        try:
            img = Image.open(image_path)
            encoded_img = self._encode_text_lsb(img, secret_text)
            encoded_img.save(output_path)
        except Exception as e:
            raise SteganographyError(f"Error hiding text in image: {e}")

    def extract_text_lsb(self, image_path: str) -> str:
        """
        Extract hidden text from image using LSB steganography.
        
        Args:
            image_path: Path to stego image
            
        Returns:
            Extracted secret text
        """
        try:
            img = Image.open(image_path)
            return self._decode_text_lsb(img)
        except Exception as e:
            raise SteganographyError(f"Error extracting text from image: {e}")

    def _encode_text_lsb(self, image: Image.Image, secret_text: str) -> Image.Image:
        """Internal function to encode text using LSB."""
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Prepare secret data
        secret_data = secret_text + "###END###"  # End marker
        binary_data = ''.join(format(ord(char), '08b') for char in secret_data)
        
        pixels = list(image.getdata())
        
        if len(binary_data) > len(pixels) * 3:
            raise SteganographyError("Secret text too large for image")
        
        # Modify pixels
        data_index = 0
        new_pixels = []
        
        for pixel in pixels:
            r, g, b = pixel
            
            if data_index < len(binary_data):
                # Modify red channel LSB
                r = (r & 0xFE) | int(binary_data[data_index])
                data_index += 1
                
            if data_index < len(binary_data):
                # Modify green channel LSB
                g = (g & 0xFE) | int(binary_data[data_index])
                data_index += 1
                
            if data_index < len(binary_data):
                # Modify blue channel LSB
                b = (b & 0xFE) | int(binary_data[data_index])
                data_index += 1
                
            new_pixels.append((r, g, b))
        
        # Create new image
        new_image = Image.new('RGB', image.size)
        new_image.putdata(new_pixels)
        return new_image

    def _decode_text_lsb(self, image: Image.Image) -> str:
        """Internal function to decode text using LSB."""
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        pixels = list(image.getdata())
        binary_data = ""
        
        # Extract LSBs
        for pixel in pixels:
            r, g, b = pixel
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)
        
        # Convert binary to text
        result = ""
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i+8]
            if len(byte) == 8:
                char = chr(int(byte, 2))
                result += char
                
                # Check for end marker
                if result.endswith("###END###"):
                    return result[:-9]  # Remove end marker
        
        raise SteganographyError("No hidden message found or corrupted data")

    @staticmethod
    def analyze_image(image_path: str) -> dict:
        """
        Analyze image for steganographic content.
        
        Args:
            image_path: Path to image
            
        Returns:
            Analysis results
        """
        if not PIL_AVAILABLE:
            raise SteganographyError("Pillow library required for image analysis")
        
        try:
            img = Image.open(image_path)
            
            analysis = {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                'capacity_bytes': (img.size[0] * img.size[1] * 3) // 8  # LSB capacity
            }
            
            return analysis
        except Exception as e:
            raise SteganographyError(f"Error analyzing image: {e}")


# Backward compatibility functions
def hide_text_lsb(image_path: str, secret_text: str, output_path: str) -> None:
    """Backward compatibility function for hiding text in image."""
    stego = ImageSteganography()
    return stego.hide_text_lsb(image_path, secret_text, output_path)


def extract_text_lsb(image_path: str) -> str:
    """Backward compatibility function for extracting text from image."""
    stego = ImageSteganography()
    return stego.extract_text_lsb(image_path)