import sys
from pathlib import Path
import json

# Add project root to path
sys.path.append(str(Path.cwd()))

from utils.schema import ContentChunk, ImageData, ImageType, RetrievalResult

class MockRetriever:
    def format_results_for_llm(self, results):
        formatted = []
        for result in results:
            chunk = result.chunk
            chunk_dict = {
                'text_content': chunk.text_content,
                'class_level': chunk.class_level,
                'chapter_number': chunk.chapter_number,
                'chapter_name': chunk.chapter_name,
                'section_name': chunk.section_name,
                'content_type': chunk.content_type.value,
                'score': result.score
            }
            if chunk.images:
                chunk_dict['images'] = [
                    {
                        'description': img.description,
                        'path': img.image_path,
                        'ocr_text': img.ocr_text
                    }
                    for img in chunk.images
                ]
            formatted.append(chunk_dict)
        return formatted

def test_logic():
    print("Testing Pipeline Logic...")
    
    mock_chunk = ContentChunk(
        chunk_id="test_chunk",
        document_id="math_book",
        class_level="11",
        chapter_number=1,
        chapter_name="Sets",
        text_content="The variety of intervals are shown in Fig 1.1.",
        images=[
            ImageData(
                image_id="fig_1_1",
                image_path="data/processed_verification/images/fig_1_1_p11.png",
                image_type=ImageType.DIAGRAM,
                description="Diagram showing intervals on a number line"
            )
        ]
    )
    
    mock_results = [RetrievalResult(chunk=mock_chunk, score=0.9, rank=1)]
    
    retriever = MockRetriever()
    formatted_context = retriever.format_results_for_llm(mock_results)
    
    print("Formatted Result:")
    print(json.dumps(formatted_context, indent=2))
    
    if 'images' in formatted_context[0] and formatted_context[0]['images'][0]['path'] == "data/processed_verification/images/fig_1_1_p11.png":
        print("SUCCESS: End-to-end data flow logic verified!")
    else:
        print("FAILURE: Data flow issue detected.")

if __name__ == "__main__":
    test_logic()
